from __future__ import annotations

import re
from abc import ABC, abstractmethod
from html import unescape
from typing import Any

import httpx

from backend.app.core.config import get_settings
from backend.app.schemas.scientific import (
    ScientificSearchRequest,
    ScientificSearchResult,
    ScientificSourceDescriptor,
)


class ScientificConnectorError(RuntimeError):
    """Raised when a scientific connector cannot complete a request."""


class BaseScientificConnector(ABC):
    source_metadata: ScientificSourceDescriptor

    def __init__(self) -> None:
        self.settings = get_settings()

    @abstractmethod
    def search(self, request: ScientificSearchRequest) -> list[ScientificSearchResult]:
        """Perform a search against an official scientific API."""

    def describe(self) -> ScientificSourceDescriptor:
        return self.source_metadata

    def _client(self) -> httpx.Client:
        headers = {"User-Agent": f"{self.settings.app_name}/0.2.0"}
        return httpx.Client(
            headers=headers,
            follow_redirects=True,
            timeout=self.settings.scientific_http_timeout_seconds,
        )

    def _request_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            with self._client() as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ScientificConnectorError(str(exc)) from exc

    def _request_text(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> str:
        try:
            with self._client() as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as exc:
            raise ScientificConnectorError(str(exc)) from exc

    @staticmethod
    def _normalize_text(value: str | None) -> str | None:
        if not value:
            return None

        cleaned = re.sub(r"<[^>]+>", " ", unescape(value))
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned or None

    @staticmethod
    def _compact_authors(authors: list[str | None]) -> list[str]:
        cleaned = []
        for author in authors:
            if author:
                normalized = re.sub(r"\s+", " ", author).strip()
                if normalized:
                    cleaned.append(normalized)
        return cleaned

    @staticmethod
    def _date_from_parts(parts: list[int] | None) -> str | None:
        if not parts:
            return None

        values = [str(part) for part in parts[:3]]
        if len(values) == 1:
            return values[0]
        if len(values) == 2:
            return f"{values[0]}-{int(values[1]):02d}"
        return f"{values[0]}-{int(values[1]):02d}-{int(values[2]):02d}"

    @staticmethod
    def _strip_doi_prefix(value: str | None) -> str | None:
        if not value:
            return None

        normalized = value.strip()
        normalized = re.sub(r"^https?://(dx\.)?doi\.org/", "", normalized, flags=re.I)
        return normalized or None

    @staticmethod
    def _strip_pmid_prefix(value: str | None) -> str | None:
        if not value:
            return None

        match = re.search(r"(\d+)", value)
        return match.group(1) if match else value.strip()
