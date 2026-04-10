from fastapi.testclient import TestClient

from backend.app.api.routes import corpus as corpus_route
from backend.app.main import app
from backend.app.schemas.corpus import (
    CorpusCreateResponse,
    CorpusDocument,
    CorpusListResponse,
    CorpusRecord,
    CorpusSourceItem,
    CorpusSourceItemsResponse,
    CorpusSourceType,
    CorpusStats,
)


def make_corpus() -> CorpusRecord:
    document = CorpusDocument(
        source_item_id="web:item-1",
        source_type=CorpusSourceType.WEB,
        title="Article",
        language="en",
        url="https://example.org/article",
        text_content="Public article text.",
    )
    return CorpusRecord(
        title="Local corpus",
        description="Example",
        stats=CorpusStats(
            document_count=1,
            word_count=3,
            character_count=len(document.text_content),
            source_types={"web": 1},
            languages={"en": 1},
        ),
        documents=[document],
    )


def test_corpus_sources_endpoint_returns_available_texts(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        corpus_route.service,
        "list_sources",
        lambda: CorpusSourceItemsResponse(
            items=[
                CorpusSourceItem(
                    source_item_id="web:item-1",
                    source_type=CorpusSourceType.WEB,
                    title="Article",
                    source_label="example.org",
                    language="en",
                    url="https://example.org/article",
                    has_text=True,
                    text_excerpt="Public article text.",
                )
            ]
        ),
    )

    response = client.get("/api/v1/corpus/sources")

    assert response.status_code == 200
    assert response.json()["items"][0]["source_type"] == "web"


def test_corpus_create_endpoint_returns_stats(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        corpus_route.service,
        "create_corpus",
        lambda payload: CorpusCreateResponse(corpus=make_corpus()),
    )

    response = client.post(
        "/api/v1/corpus/create",
        json={"title": "Local corpus", "source_item_ids": ["web:item-1"]},
    )

    assert response.status_code == 200
    assert response.json()["corpus"]["stats"]["document_count"] == 1


def test_corpus_export_text_endpoint_returns_plain_text(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(corpus_route.service, "export_text", lambda corpus_id: "Corpus text\n")

    response = client.get("/api/v1/corpus/items/corpus-1/export-text")

    assert response.status_code == 200
    assert response.text == "Corpus text\n"


def test_corpus_items_endpoint_returns_corpora(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr(
        corpus_route.service,
        "list_corpora",
        lambda: CorpusListResponse(corpora=[make_corpus()]),
    )

    response = client.get("/api/v1/corpus/items")

    assert response.status_code == 200
    assert response.json()["corpora"][0]["title"] == "Local corpus"
