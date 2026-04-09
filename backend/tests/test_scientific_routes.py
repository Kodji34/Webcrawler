from fastapi.testclient import TestClient

from backend.app.api.routes import scientific as scientific_route
from backend.app.main import app
from backend.app.schemas.scientific import (
    ScientificImportSelectionResponse,
    ScientificImportedRecord,
    ScientificSearchResponse,
    ScientificSearchResult,
    ScientificSource,
    ScientificSourceDescriptor,
)


def test_scientific_sources_endpoint_returns_supported_sources(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        scientific_route.service,
        "list_sources",
        lambda: [
            ScientificSourceDescriptor(
                key=ScientificSource.CROSSREF,
                label="Crossref",
                description="Official API",
                official_api_url="https://api.crossref.org",
                supports_date_range=True,
                supports_language=False,
                supported_identifiers=[],
                max_results_limit=50,
            )
        ],
    )

    response = client.get("/api/v1/scientific/sources")

    assert response.status_code == 200
    assert response.json()[0]["key"] == "crossref"


def test_scientific_search_endpoint_returns_normalized_results(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        scientific_route.service,
        "search",
        lambda payload: ScientificSearchResponse(
            query_log_id="q-1",
            source=payload.source,
            total_results=1,
            results=[
                ScientificSearchResult(
                    source=payload.source,
                    title="Normalized result",
                    authors=["Ada Lovelace"],
                    publication_date="2024-01-01",
                    url="https://example.org",
                    language="en",
                    document_type="article",
                    doi="10.1000/example",
                    pmid=None,
                    abstract="Preview",
                    journal="Journal",
                    keyword_used=payload.query or "",
                )
            ],
        ),
    )

    response = client.post(
        "/api/v1/scientific/search",
        json={"source": "crossref", "query": "machine learning", "max_results": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["query_log_id"] == "q-1"
    assert payload["results"][0]["title"] == "Normalized result"


def test_scientific_import_endpoint_stores_selection(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        scientific_route.service,
        "import_selection",
        lambda payload: ScientificImportSelectionResponse(
            project_name=payload.project_name,
            imported_count=1,
            records=[
                ScientificImportedRecord(
                    project_name=payload.project_name,
                    source=ScientificSource.CROSSREF,
                    title=payload.results[0].title,
                    url=payload.results[0].url,
                    keyword_used=payload.results[0].keyword_used,
                    metadata=payload.results[0],
                )
            ],
        ),
    )

    response = client.post(
        "/api/v1/scientific/import-selection",
        json={
            "project_name": "Local Research Project",
            "results": [
                {
                    "source": "crossref",
                    "title": "Imported paper",
                    "authors": ["Ada Lovelace"],
                    "publication_date": "2024-01-01",
                    "url": "https://example.org",
                    "language": "en",
                    "document_type": "article",
                    "doi": "10.1000/example",
                    "pmid": None,
                    "abstract": "Preview",
                    "journal": "Journal",
                    "keyword_used": "ml"
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["imported_count"] == 1


def test_scientific_imports_endpoint_returns_local_records(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        scientific_route.service,
        "list_imported_records",
        lambda: [
            ScientificImportedRecord(
                project_name="Local Research Project",
                source=ScientificSource.OPENALEX,
                title="Imported record",
                url="https://example.org/paper.pdf",
                keyword_used="ai",
                metadata=ScientificSearchResult(
                    source=ScientificSource.OPENALEX,
                    title="Imported record",
                    authors=["Ada Lovelace"],
                    publication_date="2024-01-01",
                    url="https://example.org",
                    language="en",
                    document_type="article",
                    doi="10.1000/example",
                    pmid=None,
                    abstract="Preview",
                    journal="Journal",
                    pdf_url="https://example.org/paper.pdf",
                    keyword_used="ai",
                ),
            )
        ],
    )

    response = client.get("/api/v1/scientific/imports")

    assert response.status_code == 200
    assert response.json()[0]["metadata"]["pdf_url"] == "https://example.org/paper.pdf"
