from __future__ import annotations

from pathlib import Path

from backend.app.connectors.pdf.base import BasePDFConnector, PDFConnectorError, PDFImportCandidate
from backend.app.schemas.pdf import PDFImportType, PDFSource


class LocalPDFConnector(BasePDFConnector):
    def import_items(
        self,
        directory_path: str,
        *,
        recursive: bool = True,
        language: str | None = None,
    ) -> list[PDFImportCandidate]:
        root = Path(directory_path).expanduser().resolve()
        if not root.exists():
            raise PDFConnectorError(f"directory does not exist: {root}")
        if not root.is_dir():
            raise PDFConnectorError(f"path is not a directory: {root}")

        pattern = "**/*.pdf" if recursive else "*.pdf"
        files = sorted(path for path in root.glob(pattern) if path.is_file())
        return [
            PDFImportCandidate(
                source=PDFSource.LOCAL_FILES,
                file_name=path.name,
                storage_path=path,
                original_path=str(path),
                import_type=PDFImportType.LOCAL,
                language=language,
            )
            for path in files
        ]
