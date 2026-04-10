from __future__ import annotations

from urllib.parse import quote_plus

from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.schemas.fulltext import FullTextAccessMode, FullTextOutcome, FullTextSource
from backend.app.schemas.scientific import ScientificImportedRecord, ScientificSource


class EuropePmcConnector(FullTextConnector):
    source = FullTextSource.EUROPE_PMC
    label = "Europe PMC / PMC"
    description = "Open access full text via the official Europe PMC REST API."
    official_url = "https://europepmc.org/RestfulWebService"
    notes = "Used for PubMed or DOI-based retrieval when Europe PMC exposes open access full text."

    def supports(self, record: ScientificImportedRecord) -> bool:
        return bool(record.pmid or record.doi or record.source == ScientificSource.PUBMED)

    def acquire(self, record: ScientificImportedRecord):
        query = None
        if record.pmid:
            query = f"EXT_ID:{record.pmid} AND SRC:MED"
        elif record.doi:
            query = f'DOI:"{record.doi}"'

        if not query:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.UNKNOWN,
                notes=["No PMID or DOI was available for Europe PMC lookup."],
            )

        encoded_query = quote_plus(query)
        with self.http_client() as client:
            response = client.get(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={encoded_query}&resultType=core&format=json&pageSize=1"
            )
            response.raise_for_status()
            payload = response.json()
            results = payload.get("resultList", {}).get("result", [])
            if not results:
                return self.build_item(
                    record,
                    outcome=FullTextOutcome.METADATA_ONLY,
                    access_mode=FullTextAccessMode.UNKNOWN,
                    notes=["Europe PMC returned metadata only for this identifier."],
                )

            result = results[0]
            pmcid = result.get("pmcid")
            if not pmcid:
                return self.build_item(
                    record,
                    outcome=FullTextOutcome.METADATA_ONLY,
                    access_mode=FullTextAccessMode.UNKNOWN,
                    notes=["Europe PMC found the record but did not expose open access full text."],
                )

            fulltext_response = client.get(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            )
            if fulltext_response.status_code == 404:
                return self.build_item(
                    record,
                    outcome=FullTextOutcome.METADATA_ONLY,
                    access_mode=FullTextAccessMode.UNKNOWN,
                    notes=["Europe PMC metadata exists but no open access fullTextXML endpoint was available."],
                )
            fulltext_response.raise_for_status()
            text_content = self.strip_xml_or_html(fulltext_response.text)
            if not text_content:
                return self.build_item(
                    record,
                    outcome=FullTextOutcome.METADATA_ONLY,
                    access_mode=FullTextAccessMode.OPEN_ACCESS,
                    full_text_url=str(fulltext_response.url),
                    notes=["Europe PMC returned open access XML, but no readable body text was extracted."],
                )

        return self.build_item(
            record,
            outcome=FullTextOutcome.FULL_TEXT_RETRIEVED,
            access_mode=FullTextAccessMode.OPEN_ACCESS,
            text_content=text_content,
            full_text_url=str(fulltext_response.url),
            license_name=result.get("license"),
            notes=["Full text retrieved from the official Europe PMC open access endpoint."],
        )
