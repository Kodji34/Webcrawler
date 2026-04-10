from __future__ import annotations

from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.schemas.fulltext import FullTextAccessMode, FullTextOutcome, FullTextSource
from backend.app.schemas.scientific import ScientificImportedRecord


class ElsevierTdmConnector(FullTextConnector):
    source = FullTextSource.ELSEVIER
    label = "ScienceDirect / Elsevier TDM"
    description = "Official authenticated Elsevier TDM access for eligible institutions."
    official_url = "https://www.elsevier.com/about/policies-and-standards/text-and-data-mining"
    requires_authentication = True
    notes = "Requires an Elsevier API key and, in many cases, an institution token for licensed full text."

    def supports(self, record: ScientificImportedRecord) -> bool:
        domain = self.extract_domain(record.url)
        pdf_domain = self.extract_domain(record.metadata.pdf_url)
        return bool(
            record.doi
            or "sciencedirect.com" in domain
            or "elsevier.com" in domain
            or "sciencedirect.com" in pdf_domain
            or "elsevier.com" in pdf_domain
        )

    def acquire(self, record: ScientificImportedRecord):
        if not record.doi:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.UNKNOWN,
                notes=["Elsevier TDM lookup needs a DOI when no direct ScienceDirect article identifier is stored."],
            )

        if not self.settings.elsevier_api_key:
            return self.build_item(
                record,
                outcome=FullTextOutcome.FULL_TEXT_NOT_AUTHORIZED,
                access_mode=FullTextAccessMode.NOT_AUTHORIZED,
                notes=["Elsevier API credentials are missing. Add ELSEVIER_API_KEY and, if needed, ELSEVIER_INSTTOKEN."],
            )

        headers = {
            "X-ELS-APIKey": self.settings.elsevier_api_key,
            "Accept": "application/xml",
        }
        if self.settings.elsevier_insttoken:
            headers["X-ELS-Insttoken"] = self.settings.elsevier_insttoken

        with self.http_client() as client:
            response = client.get(
                f"https://api.elsevier.com/content/article/doi/{record.doi}",
                headers=headers,
            )

        if response.status_code in {401, 403}:
            return self.build_item(
                record,
                outcome=FullTextOutcome.FULL_TEXT_NOT_AUTHORIZED,
                access_mode=FullTextAccessMode.NOT_AUTHORIZED,
                notes=["Elsevier rejected the request. The institution may not be entitled to TDM full text for this article."],
            )

        if response.status_code == 404:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.AUTHENTICATED_API,
                notes=["Elsevier did not return article full text for this DOI through the official TDM endpoint."],
            )

        response.raise_for_status()
        text_content = self.strip_xml_or_html(response.text)
        if not text_content:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.AUTHENTICATED_API,
                full_text_url=str(response.url),
                notes=["Elsevier responded, but no readable full text body was extracted from the official payload."],
            )

        return self.build_item(
            record,
            outcome=FullTextOutcome.FULL_TEXT_RETRIEVED,
            access_mode=FullTextAccessMode.AUTHENTICATED_API,
            text_content=text_content,
            full_text_url=str(response.url),
            notes=["Full text retrieved through Elsevier's authenticated TDM API."],
        )
