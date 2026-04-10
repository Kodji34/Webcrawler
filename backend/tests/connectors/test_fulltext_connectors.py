from httpx import Request, Response

from backend.app.connectors.fulltext.elsevier import ElsevierTdmConnector
from backend.app.connectors.fulltext.europe_pmc import EuropePmcConnector
from backend.app.core.config import Settings
from backend.app.schemas.fulltext import FullTextOutcome
from backend.app.schemas.scientific import (
    ScientificImportedRecord,
    ScientificSearchResult,
    ScientificSource,
)


class StubClient:
    def __init__(self, responses: list[Response]) -> None:
        self.responses = responses
        self.index = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, *args, **kwargs) -> Response:
        response = self.responses[self.index]
        self.index += 1
        return response


def make_record(**overrides) -> ScientificImportedRecord:
    payload = {
        "project_name": "Local Research Project",
        "source": ScientificSource.PUBMED,
        "title": "Sample article",
        "doi": "10.1000/example",
        "pmid": "123456",
        "publication_date": "2024-01-01",
        "journal": "Journal",
        "url": "https://pubmed.ncbi.nlm.nih.gov/123456/",
        "keyword_used": "ai",
        "metadata": ScientificSearchResult(
            source=ScientificSource.PUBMED,
            title="Sample article",
            authors=["Ada Lovelace"],
            publication_date="2024-01-01",
            url="https://pubmed.ncbi.nlm.nih.gov/123456/",
            language="en",
            document_type="article",
            doi="10.1000/example",
            pmid="123456",
            abstract="Preview",
            journal="Journal",
            keyword_used="ai",
        ),
    }
    payload.update(overrides)
    return ScientificImportedRecord(**payload)


def test_europe_pmc_connector_retrieves_open_access_xml(monkeypatch) -> None:
    connector = EuropePmcConnector()
    record = make_record()
    responses = [
        Response(
            200,
            request=Request("GET", "https://www.ebi.ac.uk/europepmc/webservices/rest/search"),
            json={
                "resultList": {
                    "result": [{"pmcid": "PMC12345", "license": "CC BY"}]
                }
            },
        ),
        Response(
            200,
            request=Request("GET", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12345/fullTextXML"),
            text="<article><body><p>Full text body.</p></body></article>",
        ),
    ]
    monkeypatch.setattr(connector, "http_client", lambda: StubClient(responses))

    item = connector.acquire(record)

    assert item.outcome == FullTextOutcome.FULL_TEXT_RETRIEVED
    assert item.text_content == "Full text body."
    assert item.license_name == "CC BY"


def test_elsevier_connector_requires_credentials() -> None:
    connector = ElsevierTdmConnector(
        settings=Settings(elsevier_api_key=None, elsevier_insttoken=None)
    )
    record = make_record(
        url="https://www.sciencedirect.com/science/article/pii/S123456789",
    )

    item = connector.acquire(record)

    assert item.outcome == FullTextOutcome.FULL_TEXT_NOT_AUTHORIZED
    assert "ELSEVIER_API_KEY" in item.notes[0]
