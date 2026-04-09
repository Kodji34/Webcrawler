from pathlib import Path

import fitz

from backend.app.schemas.pdf import PDFCleaningOptions, PDFExtractionMode
from backend.app.services.pdf_extraction_service import PDFExtractionService


def create_text_pdf(path: Path, *pages: str) -> None:
    document = fitz.open()
    for content in pages:
        page = document.new_page()
        page.insert_text((72, 96), content)
    document.save(path)
    document.close()


def create_blank_pdf(path: Path) -> None:
    document = fitz.open()
    document.new_page()
    document.save(path)
    document.close()


def test_native_extraction_returns_pdf_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "native.pdf"
    create_text_pdf(pdf_path, "Native extraction works.")

    service = PDFExtractionService()
    payload = service.process_pdf(
        pdf_path,
        requested_mode=PDFExtractionMode.NATIVE,
        language="en",
        cleaning_options=PDFCleaningOptions(),
    )

    assert payload.used_mode == PDFExtractionMode.NATIVE
    assert payload.raw_text is not None
    assert "Native extraction works." in payload.raw_text
    assert payload.page_count == 1


def test_blank_pdf_flags_ocr_recommendation(tmp_path: Path) -> None:
    pdf_path = tmp_path / "blank.pdf"
    create_blank_pdf(pdf_path)

    service = PDFExtractionService()
    payload = service.process_pdf(
        pdf_path,
        requested_mode=PDFExtractionMode.NATIVE,
        language=None,
        cleaning_options=PDFCleaningOptions(),
    )

    assert payload.used_mode == PDFExtractionMode.NATIVE
    assert payload.ocr_recommended is True
