from backend.app.connectors.scientific.crossref import CrossrefConnector
from backend.app.connectors.scientific.hal import HalConnector
from backend.app.connectors.scientific.openalex import OpenAlexConnector
from backend.app.connectors.scientific.pubmed import PubMedConnector
from backend.app.schemas.scientific import (
    IdentifierType,
    ScientificSearchRequest,
    ScientificSource,
)


def test_crossref_connector_normalizes_response(monkeypatch) -> None:
    connector = CrossrefConnector()
    monkeypatch.setattr(
        connector,
        "_request_json",
        lambda url, params=None: {
            "message": {
                "items": [
                    {
                        "title": ["Crossref Title"],
                        "author": [{"given": "Ada", "family": "Lovelace"}],
                        "published-online": {"date-parts": [[2024, 5, 17]]},
                        "URL": "https://doi.org/10.1000/crossref",
                        "language": "en",
                        "type": "journal-article",
                        "DOI": "10.1000/crossref",
                        "abstract": "<jats:p>Crossref abstract</jats:p>",
                        "container-title": ["Crossref Journal"],
                    }
                ]
            }
        },
    )

    results = connector.search(
        ScientificSearchRequest(source=ScientificSource.CROSSREF, query="climate"),
    )

    assert results[0].title == "Crossref Title"
    assert results[0].doi == "10.1000/crossref"
    assert results[0].journal == "Crossref Journal"


def test_openalex_connector_normalizes_response(monkeypatch) -> None:
    connector = OpenAlexConnector()
    monkeypatch.setattr(
        connector,
        "_request_json",
        lambda url, params=None: {
            "results": [
                {
                    "display_name": "OpenAlex Title",
                    "authorships": [{"author": {"display_name": "Grace Hopper"}}],
                    "publication_date": "2023-09-01",
                    "primary_location": {
                        "landing_page_url": "https://openalex.org/W1",
                        "source": {"display_name": "OpenAlex Journal"},
                    },
                    "language": "en",
                    "type_crossref": "journal-article",
                    "doi": "https://doi.org/10.1000/openalex",
                    "ids": {"pmid": "https://pubmed.ncbi.nlm.nih.gov/123456/"},
                    "abstract_inverted_index": {"OpenAlex": [0], "abstract": [1]},
                }
            ]
        },
    )

    results = connector.search(
        ScientificSearchRequest(source=ScientificSource.OPENALEX, query="biology"),
    )

    assert results[0].pmid == "123456"
    assert results[0].abstract == "OpenAlex abstract"


def test_pubmed_connector_normalizes_response(monkeypatch) -> None:
    connector = PubMedConnector()
    monkeypatch.setattr(
        connector,
        "_request_json",
        lambda url, params=None: {"esearchresult": {"idlist": ["123456"]}},
    )
    monkeypatch.setattr(
        connector,
        "_request_text",
        lambda url, params=None: """
        <PubmedArticleSet>
          <PubmedArticle>
            <MedlineCitation>
              <PMID>123456</PMID>
              <Article>
                <ArticleTitle>PubMed Title</ArticleTitle>
                <Abstract><AbstractText>PubMed abstract</AbstractText></Abstract>
                <AuthorList>
                  <Author><ForeName>Marie</ForeName><LastName>Curie</LastName></Author>
                </AuthorList>
                <Journal>
                  <Title>PubMed Journal</Title>
                  <JournalIssue><PubDate><Year>2022</Year><Month>05</Month><Day>04</Day></PubDate></JournalIssue>
                </Journal>
                <Language>eng</Language>
                <PublicationTypeList><PublicationType>Review</PublicationType></PublicationTypeList>
                <ELocationID EIdType="doi">10.1000/pubmed</ELocationID>
              </Article>
            </MedlineCitation>
          </PubmedArticle>
        </PubmedArticleSet>
        """,
    )

    results = connector.search(
        ScientificSearchRequest(
            source=ScientificSource.PUBMED,
            identifier="123456",
            identifier_type=IdentifierType.PMID,
        ),
    )

    assert results[0].title == "PubMed Title"
    assert results[0].pmid == "123456"
    assert results[0].doi == "10.1000/pubmed"


def test_hal_connector_normalizes_response(monkeypatch) -> None:
    connector = HalConnector()
    monkeypatch.setattr(
        connector,
        "_request_json",
        lambda url, params=None: {
            "response": {
                "docs": [
                    {
                        "title_s": ["HAL Title"],
                        "authFullName_s": ["Alan Turing"],
                        "producedDate_tdate": "2021-11-09",
                        "uri_s": "https://hal.science/hal-12345",
                        "language_s": "en",
                        "docType_s": "ART",
                        "doiId_s": "10.1000/hal",
                        "abstract_s": "HAL abstract",
                        "journalTitle_s": "HAL Journal",
                    }
                ]
            }
        },
    )

    results = connector.search(
        ScientificSearchRequest(source=ScientificSource.HAL, query="archives"),
    )

    assert results[0].source == ScientificSource.HAL
    assert results[0].journal == "HAL Journal"
