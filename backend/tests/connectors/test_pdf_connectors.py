from pathlib import Path

from backend.app.connectors.pdf.local_files import LocalPDFConnector
from backend.app.connectors.pdf.remote_pdf import RemotePDFConnector
from backend.app.schemas.pdf import PDFImportType, PDFImportUrlEntry


def test_local_pdf_connector_scans_pdf_files(tmp_path: Path) -> None:
    pdf_path = tmp_path / "example.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")
    (tmp_path / "ignore.txt").write_text("not a pdf", encoding="utf-8")

    connector = LocalPDFConnector()
    items = connector.import_items(str(tmp_path), recursive=False)

    assert len(items) == 1
    assert items[0].file_name == "example.pdf"
    assert items[0].original_path == str(pdf_path.resolve())


def test_remote_pdf_connector_downloads_direct_pdf(monkeypatch, tmp_path: Path) -> None:
    class FakeResponse:
        headers = {"content-type": "application/pdf"}
        content = b"%PDF-1.4\n%EOF"

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def get(self, url: str) -> FakeResponse:
            assert url == "https://example.org/paper.pdf"
            return FakeResponse()

    connector = RemotePDFConnector()
    monkeypatch.setattr(connector, "_client", lambda: FakeClient())

    items = connector.import_items(
        [PDFImportUrlEntry(url="https://example.org/paper.pdf", label="paper.pdf")],
        cache_dir=tmp_path,
        import_type=PDFImportType.REMOTE,
        language="en",
    )

    assert len(items) == 1
    assert items[0].original_url == "https://example.org/paper.pdf"
    assert items[0].storage_path.exists()
