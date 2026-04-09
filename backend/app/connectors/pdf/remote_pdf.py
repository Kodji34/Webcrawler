from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import httpx

from backend.app.connectors.pdf.base import BasePDFConnector, PDFConnectorError, PDFImportCandidate
from backend.app.core.config import get_settings
from backend.app.schemas.pdf import PDFImportType, PDFImportUrlEntry, PDFSource


class RemotePDFConnector(BasePDFConnector):
    def __init__(self) -> None:
        self.settings = get_settings()

    def _client(self) -> httpx.Client:
        return httpx.Client(
            follow_redirects=True,
            timeout=self.settings.pdf_http_timeout_seconds,
            headers={"User-Agent": f"{self.settings.app_name}/0.3.0"},
        )

    def import_items(
        self,
        entries: list[PDFImportUrlEntry],
        *,
        cache_dir: Path,
        import_type: PDFImportType,
        language: str | None = None,
    ) -> list[PDFImportCandidate]:
        cache_dir.mkdir(parents=True, exist_ok=True)
        imported: list[PDFImportCandidate] = []
        with self._client() as client:
            for index, entry in enumerate(entries, start=1):
                imported.append(
                    self._download_single(
                        client,
                        entry,
                        cache_dir=cache_dir,
                        index=index,
                        import_type=import_type,
                        language=language,
                    )
                )
        return imported

    def _download_single(
        self,
        client: httpx.Client,
        entry: PDFImportUrlEntry,
        *,
        cache_dir: Path,
        index: int,
        import_type: PDFImportType,
        language: str | None,
    ) -> PDFImportCandidate:
        try:
            response = client.get(str(entry.url))
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise PDFConnectorError(f"failed to download {entry.url}: {exc}") from exc

        content_type = response.headers.get("content-type", "").lower()
        parsed = urlparse(str(entry.url))
        inferred_name = Path(parsed.path).name or f"remote-{index}.pdf"
        if not inferred_name.lower().endswith(".pdf"):
            inferred_name = f"{inferred_name}.pdf"

        if "pdf" not in content_type and not parsed.path.lower().endswith(".pdf"):
            raise PDFConnectorError(f"URL does not appear to point to a PDF: {entry.url}")

        target_path = cache_dir / f"{index:03d}-{inferred_name}"
        target_path.write_bytes(response.content)

        source = (
            PDFSource.LINKED_SCIENTIFIC_RESULT
            if import_type == PDFImportType.LINKED_SCIENTIFIC_RESULT
            else PDFSource.REMOTE_PDF
        )
        return PDFImportCandidate(
            source=source,
            file_name=entry.label or inferred_name,
            storage_path=target_path,
            original_url=str(entry.url),
            import_type=import_type,
            language=language,
            linked_record_title=entry.linked_record_title,
        )
