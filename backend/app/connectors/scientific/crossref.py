from __future__ import annotations

from typing import Any
from urllib.parse import quote

from backend.app.connectors.scientific.base import BaseScientificConnector
from backend.app.schemas.scientific import (
    IdentifierType,
    ScientificSearchRequest,
    ScientificSearchResult,
    ScientificSource,
    ScientificSourceDescriptor,
)


class CrossrefConnector(BaseScientificConnector):
    source_metadata = ScientificSourceDescriptor(
        key=ScientificSource.CROSSREF,
        label="Crossref",
        description="Official Crossref REST API for scholarly metadata.",
        official_api_url="https://api.crossref.org",
        supports_date_range=True,
        supports_language=False,
        supported_identifiers=[IdentifierType.DOI],
    )

    def search(self, request: ScientificSearchRequest) -> list[ScientificSearchResult]:
        if request.identifier and request.identifier_type == IdentifierType.DOI:
            item = self._request_json(
                f"https://api.crossref.org/works/{quote(request.identifier, safe='')}"
            )["message"]
            return [self._normalize_item(item, request.query or request.identifier)]

        params: dict[str, Any] = {"rows": request.max_results}
        if request.query:
            params["query"] = request.query
        if self.settings.scientific_api_mailto:
            params["mailto"] = self.settings.scientific_api_mailto

        filters: list[str] = []
        if request.start_date:
            filters.append(f"from-pub-date:{request.start_date.isoformat()}")
        if request.end_date:
            filters.append(f"until-pub-date:{request.end_date.isoformat()}")
        if filters:
            params["filter"] = ",".join(filters)

        response = self._request_json("https://api.crossref.org/works", params=params)
        items = response.get("message", {}).get("items", [])
        keyword = request.query or request.identifier or ""
        return [self._normalize_item(item, keyword) for item in items]

    def _normalize_item(self, item: dict[str, Any], keyword: str) -> ScientificSearchResult:
        published = (
            item.get("published-print", {}).get("date-parts", [[]])[0]
            or item.get("published-online", {}).get("date-parts", [[]])[0]
            or item.get("created", {}).get("date-parts", [[]])[0]
        )
        pdf_url = None
        for link in item.get("link", []):
            if (link.get("content-type") or "").lower() == "application/pdf":
                pdf_url = link.get("URL")
                break
        authors = [
            " ".join(part for part in [author.get("given"), author.get("family")] if part)
            for author in item.get("author", [])
        ]
        return ScientificSearchResult(
            source=ScientificSource.CROSSREF,
            title=(item.get("title") or ["Untitled"])[0],
            authors=self._compact_authors(authors),
            publication_date=self._date_from_parts(published),
            url=item.get("URL") or "",
            language=item.get("language"),
            document_type=item.get("type"),
            doi=self._strip_doi_prefix(item.get("DOI")),
            pmid=None,
            abstract=self._normalize_text(item.get("abstract")),
            journal=(item.get("container-title") or [None])[0],
            pdf_url=pdf_url,
            keyword_used=keyword,
        )
