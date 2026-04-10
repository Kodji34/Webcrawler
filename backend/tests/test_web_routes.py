from fastapi.testclient import TestClient

from backend.app.api.routes import web as web_route
from backend.app.main import app
from backend.app.schemas.web import (
    WebImportedArticle,
    WebImportedItemsResponse,
    WebImportResponse,
    WebImportStatus,
)


def test_web_import_urls_endpoint_returns_status_items(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        web_route.service,
        "import_urls",
        lambda payload: WebImportResponse(
            imported_count=1,
            text_retrieved_count=1,
            items=[
                WebImportedArticle(
                    project_name=payload.project_name,
                    url=str(payload.entries[0].url),
                    title="News article",
                    source_domain="example.org",
                    status=WebImportStatus.TEXT_RETRIEVED,
                    text_content="A long public article body.",
                )
            ],
        ),
    )

    response = client.post(
        "/api/v1/web/import-urls",
        json={
            "project_name": "Local Research Project",
            "entries": [{"url": "https://example.org/article"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["status"] == "text_retrieved"


def test_web_items_endpoint_returns_local_imports(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        web_route.service,
        "list_items",
        lambda: WebImportedItemsResponse(
            items=[
                WebImportedArticle(
                    project_name="Local Research Project",
                    url="https://example.org/article",
                    title="Stored article",
                    status=WebImportStatus.METADATA_ONLY,
                )
            ]
        ),
    )

    response = client.get("/api/v1/web/items")

    assert response.status_code == 200
    assert response.json()["items"][0]["status"] == "metadata_only"
