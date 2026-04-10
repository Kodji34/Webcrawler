from __future__ import annotations

import json
import re
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.core.config import get_settings
from backend.app.schemas.corpus import (
    CorpusCreateRequest,
    CorpusCreateResponse,
    CorpusDocument,
    CorpusListResponse,
    CorpusRecord,
    CorpusSourceItem,
    CorpusSourceItemsResponse,
    CorpusSourceType,
    CorpusStats,
)

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


class CorpusPersistenceStore:
    def __init__(self, store_path: str | None = None) -> None:
        settings = get_settings()
        self.path = Path(store_path or settings.corpus_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _ensure_store(self) -> None:
        if not self.path.exists():
            self.path.write_text(json.dumps({"corpora": []}, indent=2), encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        self._ensure_store()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def append_corpus(self, corpus: CorpusRecord) -> None:
        with self._lock:
            payload = self._load()
            payload["corpora"].append(corpus.model_dump(mode="json"))
            self._save(payload)

    def list_corpora(self) -> list[CorpusRecord]:
        payload = self._load()
        return [CorpusRecord.model_validate(item) for item in payload.get("corpora", [])]


class CorpusService:
    def __init__(self, store: CorpusPersistenceStore | None = None) -> None:
        self.settings = get_settings()
        self.store = store or CorpusPersistenceStore()

    def list_sources(self) -> CorpusSourceItemsResponse:
        return CorpusSourceItemsResponse(items=list(self._source_items().values()))

    def list_corpora(self) -> CorpusListResponse:
        corpora = sorted(self.store.list_corpora(), key=lambda item: item.created_at, reverse=True)
        return CorpusListResponse(corpora=corpora)

    def create_corpus(self, request: CorpusCreateRequest) -> CorpusCreateResponse:
        available = self._source_items(include_text=True)
        documents: list[CorpusDocument] = []
        missing: list[str] = []

        for source_item_id in request.source_item_ids:
            item = available.get(source_item_id)
            text_content = (item or {}).get("text_content")
            if not item or not text_content:
                missing.append(source_item_id)
                continue
            documents.append(
                CorpusDocument(
                    source_item_id=source_item_id,
                    source_type=item["source_type"],
                    title=item["title"],
                    language=item.get("language"),
                    url=item.get("url"),
                    text_content=text_content,
                )
            )

        if not documents:
            raise ValueError(
                "no selected source item contains usable text; preview or extract PDF/full text/web imports first"
            )

        description = request.description
        if missing:
            description = self._append_note(
                description,
                f"Skipped {len(missing)} source item(s) without usable text.",
            )

        corpus = CorpusRecord(
            title=request.title,
            description=description,
            documents=documents,
            stats=self._stats(documents),
        )
        self.store.append_corpus(corpus)
        return CorpusCreateResponse(corpus=corpus)

    def get_corpus(self, corpus_id: str) -> CorpusRecord:
        for corpus in self.store.list_corpora():
            if corpus.corpus_id == corpus_id:
                return corpus
        raise ValueError(f"unknown corpus: {corpus_id}")

    def export_text(self, corpus_id: str) -> str:
        corpus = self.get_corpus(corpus_id)
        sections = [f"# {corpus.title}", ""]
        if corpus.description:
            sections.extend([corpus.description, ""])
        for index, document in enumerate(corpus.documents, start=1):
            sections.extend(
                [
                    f"## Document {index}: {document.title}",
                    f"source_type: {document.source_type.value}",
                    f"source_item_id: {document.source_item_id}",
                    f"url: {document.url or '-'}",
                    "",
                    document.text_content,
                    "",
                ]
            )
        return "\n".join(sections).strip() + "\n"

    def _source_items(self, *, include_text: bool = False) -> dict[str, dict[str, Any]]:
        items: dict[str, dict[str, Any]] = {}
        items.update(self._pdf_sources(include_text=include_text))
        items.update(self._fulltext_sources(include_text=include_text))
        items.update(self._web_sources(include_text=include_text))
        return items

    def _pdf_sources(self, *, include_text: bool) -> dict[str, dict[str, Any]]:
        payload = self._read_store(self.settings.pdf_store_path)
        sources: dict[str, dict[str, Any]] = {}
        for record in payload.get("saved_records", []):
            item = record.get("item", {})
            text_content = item.get("text_cleaned") or item.get("text_raw")
            source_item_id = f"pdf:{record.get('save_id')}"
            sources[source_item_id] = self._source_dict(
                source_item_id=source_item_id,
                source_type=CorpusSourceType.PDF,
                title=item.get("title") or item.get("file_name") or "PDF document",
                language=item.get("language"),
                url=item.get("original_url") or item.get("original_path"),
                text_content=text_content,
                source_label="PDF",
                include_text=include_text,
            )
        return sources

    def _fulltext_sources(self, *, include_text: bool) -> dict[str, dict[str, Any]]:
        payload = self._read_store(self.settings.fulltext_store_path)
        sources: dict[str, dict[str, Any]] = {}
        for item in payload.get("items", []):
            text_content = item.get("text_content")
            source_item_id = f"fulltext:{item.get('item_id')}"
            sources[source_item_id] = self._source_dict(
                source_item_id=source_item_id,
                source_type=CorpusSourceType.FULLTEXT,
                title=item.get("title") or "Full text item",
                language=item.get("language"),
                url=item.get("full_text_url") or item.get("landing_url"),
                text_content=text_content,
                source_label=item.get("source"),
                include_text=include_text,
                notes=item.get("notes", []),
            )
        return sources

    def _web_sources(self, *, include_text: bool) -> dict[str, dict[str, Any]]:
        payload = self._read_store(self.settings.web_store_path)
        sources: dict[str, dict[str, Any]] = {}
        for item in payload.get("items", []):
            text_content = item.get("text_content")
            source_item_id = f"web:{item.get('item_id')}"
            sources[source_item_id] = self._source_dict(
                source_item_id=source_item_id,
                source_type=CorpusSourceType.WEB,
                title=item.get("title") or item.get("label") or item.get("url") or "Web article",
                language=item.get("language"),
                url=item.get("url"),
                text_content=text_content,
                source_label=item.get("source_domain"),
                include_text=include_text,
                notes=item.get("notes", []),
            )
        return sources

    @staticmethod
    def _source_dict(
        *,
        source_item_id: str,
        source_type: CorpusSourceType,
        title: str,
        language: str | None,
        url: str | None,
        text_content: str | None,
        source_label: str | None,
        include_text: bool,
        notes: list[str] | None = None,
    ) -> dict[str, Any]:
        excerpt = " ".join(text_content.split())[:500] if text_content else None
        payload = CorpusSourceItem(
            source_item_id=source_item_id,
            source_type=source_type,
            title=title,
            source_label=source_label,
            language=language,
            url=url,
            has_text=bool(text_content),
            text_excerpt=excerpt,
            notes=notes or [],
        ).model_dump()
        if include_text:
            payload["text_content"] = text_content
        return payload

    @staticmethod
    def _read_store(path: str) -> dict[str, Any]:
        store_path = Path(path)
        if not store_path.exists():
            return {}
        return json.loads(store_path.read_text(encoding="utf-8"))

    @staticmethod
    def _stats(documents: list[CorpusDocument]) -> CorpusStats:
        source_types: dict[str, int] = {}
        languages: dict[str, int] = {}
        word_count = 0
        character_count = 0
        for document in documents:
            source_types[document.source_type.value] = source_types.get(document.source_type.value, 0) + 1
            language = document.language or "unknown"
            languages[language] = languages.get(language, 0) + 1
            word_count += len(WORD_RE.findall(document.text_content))
            character_count += len(document.text_content)
        return CorpusStats(
            document_count=len(documents),
            word_count=word_count,
            character_count=character_count,
            source_types=source_types,
            languages=languages,
        )

    @staticmethod
    def _append_note(description: str | None, note: str) -> str:
        return f"{description}\n\n{note}" if description else note
