from __future__ import annotations

from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.schemas.fulltext import FullTextAccessMode, FullTextOutcome, FullTextSource
from backend.app.schemas.scientific import ScientificImportedRecord


class OpenEditionConnector(FullTextConnector):
    source = FullTextSource.OPENEDITION
    label = "OpenEdition Journals"
    description = "OpenEdition metadata via OAI, with HTML full text only when the article page is openly accessible."
    official_url = "https://oai-openedition.readthedocs.io/en/latest/"
    notes = "OpenEdition OAI exposes metadata widely; TEI/raw full text is documented for partners. HTML retrieval stays limited to openly accessible article pages."

    def supports(self, record: ScientificImportedRecord) -> bool:
        return "journals.openedition.org" in self.extract_domain(record.url)

    def acquire(self, record: ScientificImportedRecord):
        with self.http_client() as client:
            response = client.get(record.url)

        if response.status_code in {401, 403}:
            return self.build_item(
                record,
                outcome=FullTextOutcome.FULL_TEXT_NOT_AUTHORIZED,
                access_mode=FullTextAccessMode.NOT_AUTHORIZED,
                notes=["OpenEdition denied direct access to the article body for this request."],
            )

        if response.status_code >= 400:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.UNKNOWN,
                notes=["OpenEdition metadata can still be kept, but the article page was not directly retrievable."],
            )

        body_text = self.strip_xml_or_html(response.text)
        lower_body = response.text.lower()
        has_open_license = "creativecommons.org" in lower_body or "openedition freemium" in lower_body
        if not has_open_license or len(body_text) < 1200:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.OPEN_ACCESS if has_open_license else FullTextAccessMode.UNKNOWN,
                notes=[
                    "OpenEdition metadata was retrieved, but no clearly licensed open article body could be safely extracted automatically."
                ],
            )

        return self.build_item(
            record,
            outcome=FullTextOutcome.FULL_TEXT_RETRIEVED,
            access_mode=FullTextAccessMode.OPEN_ACCESS,
            text_content=body_text,
            full_text_url=record.url,
            notes=[
                "Article HTML was retrieved from the openly accessible OpenEdition page.",
                "The extraction is heuristic and limited to pages that expose a clearly open article body.",
            ],
        )
