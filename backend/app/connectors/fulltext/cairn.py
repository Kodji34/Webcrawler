from __future__ import annotations

from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.schemas.fulltext import FullTextAccessMode, FullTextOutcome, FullTextSource
from backend.app.schemas.scientific import ScientificImportedRecord


class CairnConnector(FullTextConnector):
    source = FullTextSource.CAIRN
    label = "Cairn"
    description = "Bibliographic acquisition only unless a separate official full-text entitlement path is configured."
    official_url = "https://www.cairn.info/"
    supports_full_text = False
    notes = "This connector keeps bibliographic metadata only. No automatic full-text acquisition is attempted without a documented official entitlement channel."

    def supports(self, record: ScientificImportedRecord) -> bool:
        return "cairn.info" in self.extract_domain(record.url)

    def acquire(self, record: ScientificImportedRecord):
        return self.build_item(
            record,
            outcome=FullTextOutcome.METADATA_ONLY,
            access_mode=FullTextAccessMode.BIBLIOGRAPHIC_ONLY,
            notes=[
                "Cairn support is restricted to metadata-only handling in this phase.",
                "No public official automated full-text acquisition path is configured here.",
            ],
        )
