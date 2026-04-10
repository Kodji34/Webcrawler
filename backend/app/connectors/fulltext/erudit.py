from __future__ import annotations

from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.schemas.fulltext import FullTextAccessMode, FullTextOutcome, FullTextSource
from backend.app.schemas.scientific import ScientificImportedRecord


class EruditConnector(FullTextConnector):
    source = FullTextSource.ERUDIT
    label = "Erudit"
    description = "Open article page retrieval when Erudit exposes a readable HTML body without access restrictions."
    official_url = "https://www.erudit.org/"
    notes = "Erudit article pages may expose HTML or PDF. This connector only keeps text when the page is openly accessible and readable without bypassing restrictions."

    def supports(self, record: ScientificImportedRecord) -> bool:
        return "erudit.org" in self.extract_domain(record.url)

    def acquire(self, record: ScientificImportedRecord):
        with self.http_client() as client:
            response = client.get(record.url)

        if response.status_code in {401, 403}:
            return self.build_item(
                record,
                outcome=FullTextOutcome.FULL_TEXT_NOT_AUTHORIZED,
                access_mode=FullTextAccessMode.NOT_AUTHORIZED,
                notes=["Erudit denied direct access to the article page for this request."],
            )

        if response.status_code >= 400:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.UNKNOWN,
                notes=["Erudit metadata can be preserved, but the article page was not retrievable."],
            )

        body_text = self.strip_xml_or_html(response.text)
        lower_body = response.text.lower()
        likely_open = "open access" in lower_body or "libre acces" in lower_body or "pdf" in lower_body or "html" in lower_body
        if not likely_open or len(body_text) < 1200:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.UNKNOWN,
                notes=["Erudit exposed metadata, but no sufficiently open and readable article body was extracted automatically."],
            )

        return self.build_item(
            record,
            outcome=FullTextOutcome.FULL_TEXT_RETRIEVED,
            access_mode=FullTextAccessMode.OPEN_ACCESS,
            text_content=body_text,
            full_text_url=record.url,
            notes=[
                "Article body retrieved from an openly accessible Erudit article page.",
                "The extraction is heuristic and limited to pages with a directly readable body.",
            ],
        )
