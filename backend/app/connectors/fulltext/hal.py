from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from backend.app.connectors.fulltext.base import FullTextConnector
from backend.app.schemas.fulltext import FullTextAccessMode, FullTextOutcome, FullTextSource
from backend.app.schemas.pdf import PDFCleaningOptions, PDFExtractionMode
from backend.app.schemas.scientific import ScientificImportedRecord, ScientificSource
from backend.app.services.pdf_extraction_service import PDFExtractionService


class HalFullTextConnector(FullTextConnector):
    source = FullTextSource.HAL
    label = "HAL"
    description = "Official HAL records and deposited open files when a direct file is exposed."
    official_url = "https://api.archives-ouvertes.fr/docs/search"
    notes = "Uses HAL metadata and deposited files that are directly exposed by the repository."

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pdf_extraction_service = PDFExtractionService()

    def supports(self, record: ScientificImportedRecord) -> bool:
        domain = self.extract_domain(record.url)
        pdf_domain = self.extract_domain(record.metadata.pdf_url)
        return bool(
            record.source == ScientificSource.HAL
            or "hal.science" in domain
            or "archives-ouvertes.fr" in domain
            or "hal.science" in pdf_domain
            or "archives-ouvertes.fr" in pdf_domain
        )

    def acquire(self, record: ScientificImportedRecord):
        pdf_url = record.metadata.pdf_url
        if not pdf_url:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.OPEN_ACCESS,
                notes=["The HAL record is available, but no direct deposited file URL was exposed in metadata."],
            )

        with self.http_client() as client:
            response = client.get(pdf_url)
            if response.status_code in {401, 403}:
                return self.build_item(
                    record,
                    outcome=FullTextOutcome.FULL_TEXT_NOT_AUTHORIZED,
                    access_mode=FullTextAccessMode.NOT_AUTHORIZED,
                    full_text_url=pdf_url,
                    notes=["The deposited HAL file exists but was not publicly downloadable."],
                )
            response.raise_for_status()

        with TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "hal-document.pdf"
            pdf_path.write_bytes(response.content)
            processed = self.pdf_extraction_service.process_pdf(
                pdf_path,
                requested_mode=PDFExtractionMode.NATIVE,
                language=record.metadata.language,
                cleaning_options=PDFCleaningOptions(),
            )

        if not processed.raw_text:
            return self.build_item(
                record,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.OPEN_ACCESS,
                full_text_url=pdf_url,
                notes=["The HAL file was retrieved, but no readable text was extracted from the deposited PDF."],
            )

        notes = ["Full text extracted from a HAL deposited file exposed through repository metadata."]
        notes.extend(processed.heuristic_notes)
        return self.build_item(
            record,
            outcome=FullTextOutcome.FULL_TEXT_RETRIEVED,
            access_mode=FullTextAccessMode.OPEN_ACCESS,
            text_content=processed.raw_text,
            full_text_url=pdf_url,
            notes=notes,
        )
