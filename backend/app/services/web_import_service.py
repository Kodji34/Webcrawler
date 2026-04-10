from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlparse

import httpx

from backend.app.core.config import get_settings
from backend.app.schemas.web import (
    WebImportEntry,
    WebImportRequest,
    WebImportResponse,
    WebImportedArticle,
    WebImportedItemsResponse,
    WebImportStatus,
)

SCRIPT_STYLE_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META_DESCRIPTION_RE = re.compile(
    r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\'](.*?)["\']',
    re.IGNORECASE | re.DOTALL,
)
LANG_RE = re.compile(r"<html[^>]+lang=[\"']([^\"']+)[\"']", re.IGNORECASE)


class WebPersistenceStore:
    def __init__(self, store_path: str | None = None) -> None:
        settings = get_settings()
        self.path = Path(store_path or settings.web_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _ensure_store(self) -> None:
        if not self.path.exists():
            self.path.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        self._ensure_store()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def append_items(self, items: list[WebImportedArticle]) -> None:
        with self._lock:
            payload = self._load()
            payload["items"].extend(item.model_dump(mode="json") for item in items)
            self._save(payload)

    def list_items(self) -> list[WebImportedArticle]:
        payload = self._load()
        return [WebImportedArticle.model_validate(item) for item in payload.get("items", [])]


class WebImportService:
    def __init__(self, store: WebPersistenceStore | None = None) -> None:
        self.settings = get_settings()
        self.store = store or WebPersistenceStore()

    def list_items(self) -> WebImportedItemsResponse:
        return WebImportedItemsResponse(items=self.store.list_items())

    def import_urls(self, request: WebImportRequest) -> WebImportResponse:
        items = [self._import_entry(request.project_name, entry) for entry in request.entries]
        self.store.append_items(items)
        return WebImportResponse(
            imported_count=len(items),
            text_retrieved_count=sum(1 for item in items if item.status == WebImportStatus.TEXT_RETRIEVED),
            items=items,
        )

    def _import_entry(self, project_name: str, entry: WebImportEntry) -> WebImportedArticle:
        url = str(entry.url)
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.FAILED,
                notes=["Only public HTTP(S) article URLs are accepted."],
            )

        try:
            with httpx.Client(
                timeout=self.settings.web_http_timeout_seconds,
                follow_redirects=True,
                headers={"User-Agent": "PyCrawlerResearchStudio/0.1"},
            ) as client:
                response = client.get(url)
        except httpx.HTTPError as exc:
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.FAILED,
                notes=[f"Request failed without retrying or bypassing access controls: {exc}"],
            )

        content_type = response.headers.get("content-type", "")
        if response.status_code in {401, 402, 403}:
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.NOT_AUTHORIZED,
                content_type=content_type,
                notes=["The source denied access. No authenticated browser session or bypass is attempted."],
            )

        if response.status_code >= 400:
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.FAILED,
                content_type=content_type,
                notes=[f"The source returned HTTP {response.status_code}."],
            )

        if "pdf" in content_type.lower():
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.METADATA_ONLY,
                content_type=content_type,
                notes=["This URL points to a PDF. Use the PDF workspace for extraction and OCR."],
            )

        if "html" not in content_type.lower() and "text" not in content_type.lower():
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.METADATA_ONLY,
                content_type=content_type,
                notes=["The response is not an HTML/text article page. Metadata-only record was kept."],
            )

        title = self._extract_first(TITLE_RE, response.text)
        description = self._extract_first(META_DESCRIPTION_RE, response.text)
        language = entry.language or self._extract_first(LANG_RE, response.text)
        text_content = self._html_to_text(response.text)
        if len(text_content) < 500:
            return self._build_item(
                project_name,
                entry,
                status=WebImportStatus.METADATA_ONLY,
                title=title,
                description=description,
                language=language,
                content_type=content_type,
                notes=["The page was reachable, but no sufficiently long article text was extracted automatically."],
            )

        return self._build_item(
            project_name,
            entry,
            status=WebImportStatus.TEXT_RETRIEVED,
            title=title,
            description=description,
            language=language,
            text_content=text_content,
            content_type=content_type,
            notes=["Public article URL imported without authenticated session or access bypass."],
        )

    def _build_item(
        self,
        project_name: str,
        entry: WebImportEntry,
        *,
        status: WebImportStatus,
        title: str | None = None,
        description: str | None = None,
        language: str | None = None,
        text_content: str | None = None,
        content_type: str | None = None,
        notes: list[str] | None = None,
    ) -> WebImportedArticle:
        url = str(entry.url)
        domain = urlparse(url).netloc.lower()
        excerpt = " ".join(text_content.split())[:600] if text_content else None
        return WebImportedArticle(
            project_name=project_name,
            url=url,
            label=entry.label,
            title=title or entry.label,
            description=description,
            language=language,
            source_domain=domain,
            status=status,
            text_content=text_content,
            excerpt=excerpt,
            content_type=content_type,
            notes=notes or [],
        )

    @staticmethod
    def _html_to_text(payload: str) -> str:
        without_scripts = SCRIPT_STYLE_RE.sub(" ", payload)
        without_tags = TAG_RE.sub(" ", without_scripts)
        return WHITESPACE_RE.sub(" ", unescape(without_tags)).strip()

    @staticmethod
    def _extract_first(pattern: re.Pattern[str], payload: str) -> str | None:
        match = pattern.search(payload)
        if not match:
            return None
        return WHITESPACE_RE.sub(" ", unescape(match.group(1))).strip()
