from __future__ import annotations

from typing import Any

from backend.app.connectors.scientific.base import BaseScientificConnector
from backend.app.schemas.scientific import (
    IdentifierType,
    ScientificSearchRequest,
    ScientificSearchResult,
    ScientificSource,
    ScientificSourceDescriptor,
)


class HalConnector(BaseScientificConnector):
    source_metadata = ScientificSourceDescriptor(
        key=ScientificSource.HAL,
        label="HAL",
        description="Official HAL search API for open archive records.",
        official_api_url="https://api.archives-ouvertes.fr/search/",
        supports_date_range=True,
        supports_language=True,
        supported_identifiers=[IdentifierType.DOI, IdentifierType.HAL_ID],
    )

    def search(self, request: ScientificSearchRequest) -> list[ScientificSearchResult]:
        params: dict[str, Any] = {
            "wt": "json",
            "rows": request.max_results,
            "fl": ",".join(
                [
                    "title_s",
                    "authFullName_s",
                    "producedDate_tdate",
                    "uri_s",
                    "language_s",
                    "docType_s",
                    "doiId_s",
                    "abstract_s",
                    "journalTitle_s",
                    "halId_s",
                    "fileMain_s",
                ]
            ),
            "q": self._build_query(request),
        }
        filters: list[str] = []
        if request.language:
            filters.append(f'language_s:"{request.language.lower()}"')
        if request.start_date or request.end_date:
            start_year = request.start_date.year if request.start_date else 1900
            end_year = request.end_date.year if request.end_date else 2100
            filters.append(f"producedDateY_i:[{start_year} TO {end_year}]")
        if filters:
            params["fq"] = filters

        response = self._request_json("https://api.archives-ouvertes.fr/search/", params=params)
        docs = response.get("response", {}).get("docs", [])
        keyword = request.query or request.identifier or ""
        return [self._normalize_item(item, keyword) for item in docs]

    def _build_query(self, request: ScientificSearchRequest) -> str:
        if request.identifier and request.identifier_type == IdentifierType.DOI:
            return f'doiId_s:"{self._strip_doi_prefix(request.identifier)}"'
        if request.identifier and request.identifier_type == IdentifierType.HAL_ID:
            return f'halId_s:"{request.identifier.strip()}"'
        return request.query or "*:*"

    def _normalize_item(self, item: dict[str, Any], keyword: str) -> ScientificSearchResult:
        title = item.get("title_s")
        if isinstance(title, list):
            title = title[0] if title else "Untitled"
        journal = item.get("journalTitle_s")
        if isinstance(journal, list):
            journal = journal[0] if journal else None
        abstract = item.get("abstract_s")
        if isinstance(abstract, list):
            abstract = abstract[0] if abstract else None
        doi = item.get("doiId_s")
        if isinstance(doi, list):
            doi = doi[0] if doi else None
        language = item.get("language_s")
        if isinstance(language, list):
            language = language[0] if language else None
        uri = item.get("uri_s")
        if isinstance(uri, list):
            uri = uri[0] if uri else ""
        pdf_url = item.get("fileMain_s")
        if isinstance(pdf_url, list):
            pdf_url = pdf_url[0] if pdf_url else None

        return ScientificSearchResult(
            source=ScientificSource.HAL,
            title=title or "Untitled",
            authors=self._compact_authors(item.get("authFullName_s", [])),
            publication_date=item.get("producedDate_tdate"),
            url=uri or "",
            language=language,
            document_type=item.get("docType_s"),
            doi=self._strip_doi_prefix(doi),
            pmid=None,
            abstract=self._normalize_text(abstract),
            journal=journal,
            pdf_url=pdf_url,
            keyword_used=keyword,
        )
