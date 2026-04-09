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


class OpenAlexConnector(BaseScientificConnector):
    source_metadata = ScientificSourceDescriptor(
        key=ScientificSource.OPENALEX,
        label="OpenAlex",
        description="Official OpenAlex API for open scholarly works metadata.",
        official_api_url="https://api.openalex.org",
        supports_date_range=True,
        supports_language=True,
        supported_identifiers=[IdentifierType.DOI, IdentifierType.PMID],
    )

    def search(self, request: ScientificSearchRequest) -> list[ScientificSearchResult]:
        params: dict[str, Any] = {"per-page": request.max_results}
        if self.settings.scientific_api_mailto:
            params["mailto"] = self.settings.scientific_api_mailto

        filters: list[str] = []
        if request.start_date:
            filters.append(f"from_publication_date:{request.start_date.isoformat()}")
        if request.end_date:
            filters.append(f"to_publication_date:{request.end_date.isoformat()}")
        if request.language:
            filters.append(f"language:{request.language.lower()}")
        if request.identifier and request.identifier_type == IdentifierType.DOI:
            filters.append(f"doi:https://doi.org/{self._strip_doi_prefix(request.identifier)}")
        if request.identifier and request.identifier_type == IdentifierType.PMID:
            filters.append(
                f"pmid:https://pubmed.ncbi.nlm.nih.gov/{self._strip_pmid_prefix(request.identifier)}/"
            )
        if filters:
            params["filter"] = ",".join(filters)
        if request.query:
            params["search"] = request.query
        elif request.identifier and request.identifier_type not in {
            IdentifierType.DOI,
            IdentifierType.PMID,
        }:
            params["search"] = request.identifier

        response = self._request_json("https://api.openalex.org/works", params=params)
        items = response.get("results", [])
        keyword = request.query or request.identifier or ""
        return [self._normalize_item(item, keyword) for item in items]

    def _normalize_item(self, item: dict[str, Any], keyword: str) -> ScientificSearchResult:
        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in item.get("authorships", [])
        ]
        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        best_oa_location = item.get("best_oa_location") or {}
        return ScientificSearchResult(
            source=ScientificSource.OPENALEX,
            title=item.get("display_name") or "Untitled",
            authors=self._compact_authors(authors),
            publication_date=item.get("publication_date"),
            url=primary_location.get("landing_page_url") or item.get("id") or "",
            language=item.get("language"),
            document_type=item.get("type_crossref") or item.get("type"),
            doi=self._strip_doi_prefix(item.get("doi")),
            pmid=self._strip_pmid_prefix((item.get("ids") or {}).get("pmid")),
            abstract=self._abstract_from_inverted_index(item.get("abstract_inverted_index")),
            journal=source.get("display_name"),
            pdf_url=best_oa_location.get("pdf_url"),
            keyword_used=keyword,
        )

    def _abstract_from_inverted_index(
        self,
        inverted_index: dict[str, list[int]] | None,
    ) -> str | None:
        if not inverted_index:
            return None

        positions: dict[int, str] = {}
        for token, indexes in inverted_index.items():
            for index in indexes:
                positions[index] = token
        return " ".join(token for _, token in sorted(positions.items())) or None
