from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from backend.app.schemas.pdf import PDFImportType, PDFSource


class PDFConnectorError(RuntimeError):
    """Raised when a PDF connector cannot complete an import."""


@dataclass(slots=True)
class PDFImportCandidate:
    source: PDFSource
    file_name: str
    storage_path: Path
    import_type: PDFImportType
    original_path: str | None = None
    original_url: str | None = None
    language: str | None = None
    linked_record_title: str | None = None


class BasePDFConnector(ABC):
    @abstractmethod
    def import_items(self, *args: object, **kwargs: object) -> list[PDFImportCandidate]:
        """Import PDF candidates from an external source."""
