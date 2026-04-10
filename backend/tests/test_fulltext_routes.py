from fastapi.testclient import TestClient

from backend.app.api.routes import fulltext as fulltext_route
from backend.app.main import app
from backend.app.schemas.fulltext import (
    FullTextAccessMode,
    FullTextAcquireImportsResponse,
    FullTextAcquisitionItem,
    FullTextItemsResponse,
    FullTextOutcome,
    FullTextSource,
    FullTextSourceDescriptor,
)


def test_fulltext_sources_endpoint_returns_descriptors(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        fulltext_route.service,
        "list_sources",
        lambda: [
            FullTextSourceDescriptor(
                key=FullTextSource.EUROPE_PMC,
                label="Europe PMC / PMC",
                description="Official OA",
                official_url="https://europepmc.org/RestfulWebService",
                requires_authentication=False,
                supports_full_text=True,
                notes="OA only",
            )
        ],
    )

    response = client.get("/api/v1/fulltext/sources")

    assert response.status_code == 200
    assert response.json()[0]["key"] == "europe_pmc"


def test_fulltext_acquire_imports_endpoint_returns_status_items(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        fulltext_route.service,
        "acquire_imports",
        lambda payload: FullTextAcquireImportsResponse(
            requested_count=len(payload.import_ids),
            acquired_count=1,
            items=[
                FullTextAcquisitionItem(
                    scientific_import_id=payload.import_ids[0],
                    source=FullTextSource.HAL,
                    outcome=FullTextOutcome.FULL_TEXT_RETRIEVED,
                    access_mode=FullTextAccessMode.OPEN_ACCESS,
                    title="Imported HAL article",
                    landing_url="https://hal.science/hal-123",
                    text_content="Full text body",
                )
            ],
        ),
    )

    response = client.post(
        "/api/v1/fulltext/acquire-imports",
        json={"import_ids": ["import-1"]},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["outcome"] == "full_text_retrieved"


def test_fulltext_items_endpoint_returns_persisted_items(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        fulltext_route.service,
        "list_items",
        lambda: FullTextItemsResponse(
            items=[
                FullTextAcquisitionItem(
                    scientific_import_id="import-1",
                    source=FullTextSource.CAIRN,
                    outcome=FullTextOutcome.METADATA_ONLY,
                    access_mode=FullTextAccessMode.BIBLIOGRAPHIC_ONLY,
                    title="Cairn record",
                    landing_url="https://www.cairn.info/revue-example.htm",
                )
            ]
        ),
    )

    response = client.get("/api/v1/fulltext/items")

    assert response.status_code == 200
    assert response.json()["items"][0]["access_mode"] == "bibliographic_only"
