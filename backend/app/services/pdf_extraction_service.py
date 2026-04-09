from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import shutil

from backend.app.schemas.pdf import (
    PDFCleaningOptions,
    PDFDependencyStatus,
    PDFExtractionMode,
    PDFExtractionStatus,
)
from backend.app.services.pdf_cleaning_service import PDFCleaningService

try:  # pragma: no cover - exercised through dependency status
    import fitz
except ImportError:  # pragma: no cover - depends on local environment
    fitz = None

try:  # pragma: no cover - exercised through dependency status
    import pdfplumber
except ImportError:  # pragma: no cover - depends on local environment
    pdfplumber = None

try:  # pragma: no cover - exercised through dependency status
    import pytesseract
except ImportError:  # pragma: no cover - depends on local environment
    pytesseract = None

try:  # pragma: no cover - exercised through dependency status
    from PIL import Image
except ImportError:  # pragma: no cover - depends on local environment
    Image = None


@dataclass(slots=True)
class PDFProcessedDocument:
    page_count: int | None
    title: str | None
    author: str | None
    raw_text: str | None
    cleaned_text: str | None
    preview_excerpt: str | None
    used_mode: PDFExtractionMode | None
    status: PDFExtractionStatus
    has_ocr: bool
    ocr_recommended: bool
    dependency_messages: list[str]
    heuristic_notes: list[str]


class PDFExtractionService:
    def __init__(self, cleaning_service: PDFCleaningService | None = None) -> None:
        self.cleaning_service = cleaning_service or PDFCleaningService()

    def dependency_status(self) -> PDFDependencyStatus:
        messages: list[str] = []
        if fitz is None:
            messages.append("PyMuPDF is not installed. PDF extraction is unavailable.")
        if pdfplumber is None:
            messages.append("pdfplumber is not installed. Native extraction fallback is unavailable.")
        if pytesseract is None:
            messages.append("pytesseract is not installed. OCR requires pytesseract and Tesseract.")
        if Image is None:
            messages.append("Pillow is not installed. OCR image conversion is unavailable.")
        if shutil.which("tesseract") is None:
            messages.append("Tesseract is not available on PATH. OCR requests will stay unavailable.")
        if shutil.which("ocrmypdf") is None:
            messages.append("OCRmyPDF is not available on PATH. The app uses pytesseract-based OCR only.")

        return PDFDependencyStatus(
            pymupdf_available=fitz is not None,
            pdfplumber_available=pdfplumber is not None,
            pytesseract_available=pytesseract is not None and Image is not None,
            tesseract_available=shutil.which("tesseract") is not None,
            ocrmypdf_available=shutil.which("ocrmypdf") is not None,
            messages=messages,
        )

    def inspect_pdf(self, pdf_path: Path) -> tuple[int | None, str | None, str | None]:
        if fitz is None:
            return None, None, None

        with fitz.open(pdf_path) as document:
            metadata = document.metadata or {}
            return len(document), metadata.get("title"), metadata.get("author")

    def process_pdf(
        self,
        pdf_path: Path,
        *,
        requested_mode: PDFExtractionMode,
        language: str | None,
        cleaning_options: PDFCleaningOptions,
    ) -> PDFProcessedDocument:
        dependencies = self.dependency_status()
        page_count, title, author = self.inspect_pdf(pdf_path)
        heuristic_notes: list[str] = []

        if not dependencies.pymupdf_available:
            return PDFProcessedDocument(
                page_count=page_count,
                title=title,
                author=author,
                raw_text=None,
                cleaned_text=None,
                preview_excerpt=None,
                used_mode=None,
                status=PDFExtractionStatus.DEPENDENCY_MISSING,
                has_ocr=False,
                ocr_recommended=False,
                dependency_messages=dependencies.messages,
                heuristic_notes=["PyMuPDF is required before any PDF extraction can run."],
            )

        native_pages = self._extract_native_pages(pdf_path)
        raw_native_text = self._merge_pages(native_pages)
        ocr_recommended = self._ocr_recommended(native_pages)
        if ocr_recommended:
            heuristic_notes.append(
                "Native extraction returned very little text; OCR is recommended when available."
            )

        if requested_mode == PDFExtractionMode.NATIVE:
            cleaned_text, cleaning_notes = self.cleaning_service.clean_text(
                native_pages,
                cleaning_options,
            )
            heuristic_notes.extend(cleaning_notes)
            return PDFProcessedDocument(
                page_count=page_count,
                title=title,
                author=author,
                raw_text=raw_native_text,
                cleaned_text=cleaned_text,
                preview_excerpt=self._preview_excerpt(cleaned_text or raw_native_text),
                used_mode=PDFExtractionMode.NATIVE,
                status=PDFExtractionStatus.READY,
                has_ocr=False,
                ocr_recommended=ocr_recommended,
                dependency_messages=dependencies.messages,
                heuristic_notes=heuristic_notes,
            )

        if requested_mode == PDFExtractionMode.OCR:
            if not self._ocr_ready(dependencies):
                return PDFProcessedDocument(
                    page_count=page_count,
                    title=title,
                    author=author,
                    raw_text=raw_native_text,
                    cleaned_text=None,
                    preview_excerpt=self._preview_excerpt(raw_native_text),
                    used_mode=None,
                    status=PDFExtractionStatus.DEPENDENCY_MISSING,
                    has_ocr=False,
                    ocr_recommended=True,
                    dependency_messages=dependencies.messages,
                    heuristic_notes=heuristic_notes,
                )
            return self._process_with_ocr(
                pdf_path,
                page_count=page_count,
                title=title,
                author=author,
                language=language,
                cleaning_options=cleaning_options,
                dependencies=dependencies,
                heuristic_notes=heuristic_notes,
            )

        if ocr_recommended and self._ocr_ready(dependencies):
            return self._process_with_ocr(
                pdf_path,
                page_count=page_count,
                title=title,
                author=author,
                language=language,
                cleaning_options=cleaning_options,
                dependencies=dependencies,
                heuristic_notes=heuristic_notes,
            )

        status = PDFExtractionStatus.READY
        if ocr_recommended and not self._ocr_ready(dependencies):
            status = PDFExtractionStatus.DEPENDENCY_MISSING
        cleaned_text, cleaning_notes = self.cleaning_service.clean_text(
            native_pages,
            cleaning_options,
        )
        heuristic_notes.extend(cleaning_notes)
        return PDFProcessedDocument(
            page_count=page_count,
            title=title,
            author=author,
            raw_text=raw_native_text,
            cleaned_text=cleaned_text,
            preview_excerpt=self._preview_excerpt(cleaned_text or raw_native_text),
            used_mode=PDFExtractionMode.NATIVE,
            status=status,
            has_ocr=False,
            ocr_recommended=ocr_recommended,
            dependency_messages=dependencies.messages,
            heuristic_notes=heuristic_notes,
        )

    def _process_with_ocr(
        self,
        pdf_path: Path,
        *,
        page_count: int | None,
        title: str | None,
        author: str | None,
        language: str | None,
        cleaning_options: PDFCleaningOptions,
        dependencies: PDFDependencyStatus,
        heuristic_notes: list[str],
    ) -> PDFProcessedDocument:
        ocr_pages = self._extract_ocr_pages(pdf_path, language=language)
        raw_text = self._merge_pages(ocr_pages)
        cleaned_text, cleaning_notes = self.cleaning_service.clean_text(
            ocr_pages,
            cleaning_options,
        )
        notes = list(heuristic_notes)
        notes.extend(cleaning_notes)
        notes.append("OCR extraction used pytesseract with rendered page images.")
        return PDFProcessedDocument(
            page_count=page_count,
            title=title,
            author=author,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            preview_excerpt=self._preview_excerpt(cleaned_text or raw_text),
            used_mode=PDFExtractionMode.OCR,
            status=PDFExtractionStatus.READY,
            has_ocr=True,
            ocr_recommended=True,
            dependency_messages=dependencies.messages,
            heuristic_notes=notes,
        )

    def _extract_native_pages(self, pdf_path: Path) -> list[str]:
        if fitz is None:
            return []

        fallback_pages = []
        if pdfplumber is not None:
            with pdfplumber.open(str(pdf_path)) as fallback_document:
                fallback_pages = [
                    (page.extract_text() or "").strip() for page in fallback_document.pages
                ]

        pages: list[str] = []
        with fitz.open(pdf_path) as document:
            for index, page in enumerate(document):
                text = page.get_text("text", sort=True).strip()
                if not text and index < len(fallback_pages):
                    text = fallback_pages[index]
                pages.append(text)
        return pages

    def _extract_ocr_pages(self, pdf_path: Path, *, language: str | None) -> list[str]:
        if fitz is None or pytesseract is None or Image is None:
            return []

        mapped_language = self._map_tesseract_language(language)
        pages: list[str] = []
        with fitz.open(pdf_path) as document:
            for page in document:
                pixmap = page.get_pixmap(dpi=180, alpha=False)
                image = Image.open(BytesIO(pixmap.tobytes("png")))
                pages.append(pytesseract.image_to_string(image, lang=mapped_language).strip())
        return pages

    @staticmethod
    def _merge_pages(page_texts: list[str]) -> str | None:
        text = "\n\n".join(text for text in page_texts if text.strip()).strip()
        return text or None

    @staticmethod
    def _ocr_recommended(page_texts: list[str]) -> bool:
        joined = "\n".join(page_texts).strip()
        if not joined:
            return True

        non_empty_pages = sum(1 for page in page_texts if page.strip())
        average_chars = len(joined) / max(1, len(page_texts))
        if non_empty_pages <= max(1, len(page_texts) // 3):
            return True
        return len(joined) < 200 or average_chars < 80

    @staticmethod
    def _preview_excerpt(text: str | None) -> str | None:
        if not text:
            return None
        excerpt = " ".join(text.split())
        return excerpt[:500]

    @staticmethod
    def _map_tesseract_language(language: str | None) -> str:
        mapping = {
            None: "eng",
            "en": "eng",
            "eng": "eng",
            "fr": "fra",
            "fra": "fra",
            "fre": "fra",
        }
        return mapping.get(language.lower(), language.lower()) if language else "eng"

    @staticmethod
    def _ocr_ready(dependencies: PDFDependencyStatus) -> bool:
        return (
            dependencies.pymupdf_available
            and dependencies.pytesseract_available
            and dependencies.tesseract_available
        )
