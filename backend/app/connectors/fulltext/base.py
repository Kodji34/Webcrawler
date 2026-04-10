from __future__ import annotations

import re
from html import unescape
from typing import Final
from urllib.parse import urlparse

import httpx

from backend.app.core.config import Settings, get_settings
from backend.app.schemas.fulltext import (
    FullTextAccessMode,
    FullTextAcquisitionItem,
    FullTextOutcome,
    FullTextSource,
    FullTextSourceDescriptor,
)
from backend.app.schemas.scientific import ScientificImportedRecord

WHITESPACE_RE: Final = re.compile(r"\s+")
SCRIPT_STYLE_RE: Final = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE: Final = re.compile(r"<[^>]+>")


class FullTextConnector:
    source: FullTextSource
    label: str
    description: str
    official_url: str
    requires_authentication: bool = False
    supports_full_text: bool = True
    notes: str = ""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def describe(self) -> FullTextSourceDescriptor:
        return FullTextSourceDescriptor(
            key=self.source,
            label=self.label,
            description=self.description,
            official_url=self.official_url,
            requires_authentication=self.requires_authentication,
            supports_full_text=self.supports_full_text,
            notes=self.notes,
        )

    def supports(self, record: ScientificImportedRecord) -> bool:
        raise NotImplementedError

    def acquire(self, record: ScientificImportedRecord) -> FullTextAcquisitionItem:
        raise NotImplementedError

    def build_item(
        self,
        record: ScientificImportedRecord,
        *,
        outcome: FullTextOutcome,
        access_mode: FullTextAccessMode,
        text_content: str | None = None,
        full_text_url: str | None = None,
        license_name: str | None = None,
        notes: list[str] | None = None,
    ) -> FullTextAcquisitionItem:
        excerpt = None
        if text_content:
            excerpt = " ".join(text_content.split())[:600]

        return FullTextAcquisitionItem(
            scientific_import_id=record.import_id,
            source=self.source,
            outcome=outcome,
            access_mode=access_mode,
            title=record.title,
            doi=record.doi,
            pmid=record.pmid,
            landing_url=record.url,
            full_text_url=full_text_url,
            license_name=license_name,
            language=record.metadata.language,
            journal=record.journal,
            text_content=text_content,
            excerpt=excerpt,
            notes=notes or [],
        )

    def http_client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.settings.fulltext_http_timeout_seconds,
            headers={"User-Agent": "PyCrawlerResearchStudio/0.1"},
            follow_redirects=True,
        )

    @staticmethod
    def extract_domain(url: str | None) -> str:
        if not url:
            return ""
        return urlparse(url).netloc.lower()

    @staticmethod
    def strip_xml_or_html(payload: str) -> str:
        without_scripts = SCRIPT_STYLE_RE.sub(" ", payload)
        without_tags = TAG_RE.sub(" ", without_scripts)
        return WHITESPACE_RE.sub(" ", unescape(without_tags)).strip()
