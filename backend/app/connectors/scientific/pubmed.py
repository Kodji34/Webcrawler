from __future__ import annotations

from typing import Any
from xml.etree import ElementTree

from backend.app.connectors.scientific.base import BaseScientificConnector
from backend.app.schemas.scientific import (
    IdentifierType,
    ScientificSearchRequest,
    ScientificSearchResult,
    ScientificSource,
    ScientificSourceDescriptor,
)


class PubMedConnector(BaseScientificConnector):
    source_metadata = ScientificSourceDescriptor(
        key=ScientificSource.PUBMED,
        label="PubMed",
        description="Official NCBI E-utilities for PubMed records.",
        official_api_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        supports_date_range=True,
        supports_language=True,
        supported_identifiers=[IdentifierType.DOI, IdentifierType.PMID],
    )

    def search(self, request: ScientificSearchRequest) -> list[ScientificSearchResult]:
        search_params: dict[str, Any] = {
            "db": "pubmed",
            "retmode": "json",
            "retmax": request.max_results,
            "term": self._build_term(request),
        }
        if request.start_date:
            search_params["datetype"] = "pdat"
            search_params["mindate"] = request.start_date.isoformat()
        if request.end_date:
            search_params["datetype"] = "pdat"
            search_params["maxdate"] = request.end_date.isoformat()
        if self.settings.scientific_api_mailto:
            search_params["email"] = self.settings.scientific_api_mailto
            search_params["tool"] = "PyCrawlerResearchStudio"

        search_payload = self._request_json(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params=search_params,
        )
        identifiers = search_payload.get("esearchresult", {}).get("idlist", [])
        if not identifiers:
            return []

        fetch_payload = self._request_text(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={
                "db": "pubmed",
                "retmode": "xml",
                "id": ",".join(identifiers),
            },
        )
        keyword = request.query or request.identifier or ""
        root = ElementTree.fromstring(fetch_payload)
        return [
            self._normalize_article(article, keyword)
            for article in root.findall(".//PubmedArticle")
        ]

    def _build_term(self, request: ScientificSearchRequest) -> str:
        if request.identifier and request.identifier_type == IdentifierType.PMID:
            term = f"{self._strip_pmid_prefix(request.identifier)}[PMID]"
        elif request.identifier and request.identifier_type == IdentifierType.DOI:
            term = f"{self._strip_doi_prefix(request.identifier)}[DOI]"
        else:
            term = request.query or ""

        if request.language:
            term = f"({term}) AND {self._language_query(request.language)}"
        return term

    @staticmethod
    def _language_query(language: str) -> str:
        mapping = {"en": "english[Language]", "fr": "french[Language]"}
        return mapping.get(language.lower(), f"{language}[Language]")

    def _normalize_article(
        self,
        article: ElementTree.Element,
        keyword: str,
    ) -> ScientificSearchResult:
        medline = article.find("MedlineCitation")
        article_node = medline.find("./Article") if medline is not None else None
        pmid = self._node_text(medline.find("PMID")) if medline is not None else None
        title = self._node_text(article_node.find("ArticleTitle")) if article_node is not None else None
        abstract = None
        if article_node is not None:
            abstract_sections = article_node.findall("./Abstract/AbstractText")
            abstract = " ".join(
                part
                for section in abstract_sections
                for part in [self._node_text(section)]
                if part
            ) or None

        authors = []
        if article_node is not None:
            for author in article_node.findall("./AuthorList/Author"):
                collective = self._node_text(author.find("CollectiveName"))
                if collective:
                    authors.append(collective)
                    continue
                first = self._node_text(author.find("ForeName"))
                last = self._node_text(author.find("LastName"))
                authors.append(" ".join(part for part in [first, last] if part))

        doi = None
        if article_node is not None:
            for identifier in article_node.findall("./ELocationID"):
                if identifier.attrib.get("EIdType", "").lower() == "doi":
                    doi = self._node_text(identifier)
                    break
        if not doi:
            for identifier in article.findall(".//ArticleId"):
                if identifier.attrib.get("IdType", "").lower() == "doi":
                    doi = self._node_text(identifier)
                    break

        document_type = None
        if article_node is not None:
            document_type = self._node_text(article_node.find("./PublicationTypeList/PublicationType"))

        publication_date = self._pub_date(article_node)
        journal = self._node_text(article_node.find("./Journal/Title")) if article_node is not None else None
        language = self._node_text(article_node.find("Language")) if article_node is not None else None

        return ScientificSearchResult(
            source=ScientificSource.PUBMED,
            title=title or "Untitled",
            authors=self._compact_authors(authors),
            publication_date=publication_date,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            language=language,
            document_type=document_type,
            doi=self._strip_doi_prefix(doi),
            pmid=self._strip_pmid_prefix(pmid),
            abstract=self._normalize_text(abstract),
            journal=journal,
            pdf_url=None,
            keyword_used=keyword,
        )

    def _pub_date(self, article_node: ElementTree.Element | None) -> str | None:
        if article_node is None:
            return None

        article_date = article_node.find("./ArticleDate")
        if article_date is not None:
            year = self._node_text(article_date.find("Year"))
            month = self._node_text(article_date.find("Month"))
            day = self._node_text(article_date.find("Day"))
            if year and month and day:
                return f"{year}-{int(month):02d}-{int(day):02d}"

        pub_date = article_node.find("./Journal/JournalIssue/PubDate")
        if pub_date is None:
            return None
        year = self._node_text(pub_date.find("Year"))
        month = self._node_text(pub_date.find("Month"))
        day = self._node_text(pub_date.find("Day"))
        medline_date = self._node_text(pub_date.find("MedlineDate"))
        if year and month and day and month.isdigit():
            return f"{year}-{int(month):02d}-{int(day):02d}"
        if year and month and month.isdigit():
            return f"{year}-{int(month):02d}"
        return year or medline_date

    @staticmethod
    def _node_text(node: ElementTree.Element | None) -> str | None:
        if node is None:
            return None
        return "".join(node.itertext()).strip() or None
