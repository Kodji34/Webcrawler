from pathlib import Path

import fitz
from fastapi.testclient import TestClient

from backend.app.api.routes import pdf as pdf_route
from backend.app.main import app
from backend.app.services.pdf_ingestion_service import PDFIngestionService, PDFPersistenceStore


def create_text_pdf(path: Path, text: str) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 96), text)
    document.save(path)
    document.close()


def build_service(tmp_path: Path) -> PDFIngestionService:
    store = PDFPersistenceStore(store_path=str(tmp_path / "pdf_store.json"))
    service = PDFIngestionService(store=store)
    service.download_dir = tmp_path / "pdf_cache"
    service.download_dir.mkdir(parents=True, exist_ok=True)
    return service


def test_pdf_routes_cover_local_import_preview_extract_and_save(
    monkeypatch,
    tmp_path: Path,
) -> None:
    client = TestClient(app)
    service = build_service(tmp_path)
    monkeypatch.setattr(pdf_route, "service", service)

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    pdf_path = source_dir / "paper.pdf"
    create_text_pdf(pdf_path, "PDF route extraction works.")

    import_response = client.post(
        "/api/v1/pdf/import-local",
        json={"directory_path": str(source_dir), "recursive": True, "language": "en"},
    )

    assert import_response.status_code == 200
    imported_item = import_response.json()["items"][0]
    item_id = imported_item["id"]

    items_response = client.get("/api/v1/pdf/items")
    assert items_response.status_code == 200
    assert items_response.json()["items"][0]["file_name"] == "paper.pdf"

    preview_response = client.post(
        "/api/v1/pdf/preview",
        json={
            "item_id": item_id,
            "extraction_mode": "native",
            "cleaning_options": {"generate_cleaned_text": False},
        },
    )
    assert preview_response.status_code == 200
    assert "PDF route extraction works." in preview_response.json()["item"]["text_raw"]

    extract_response = client.post(
        "/api/v1/pdf/extract",
        json={
            "item_ids": [item_id],
            "extraction_mode": "native",
            "cleaning_options": {"generate_cleaned_text": True, "normalize_whitespace": True},
        },
    )
    assert extract_response.status_code == 200
    job_id = extract_response.json()["job"]["job_id"]

    job_response = client.get(f"/api/v1/pdf/jobs/{job_id}")
    assert job_response.status_code == 200
    assert job_response.json()["processed_count"] == 1

    save_response = client.post(
        "/api/v1/pdf/save-selection",
        json={"project_name": "PDF Project", "item_ids": [item_id]},
    )
    assert save_response.status_code == 200
    assert save_response.json()["saved_count"] == 1
