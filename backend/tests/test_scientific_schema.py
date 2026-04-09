import pytest
from pydantic import ValidationError

from backend.app.schemas.scientific import (
    ScientificSearchRequest,
    ScientificSearchResult,
    ScientificSource,
)


def test_scientific_search_request_requires_query_or_identifier() -> None:
    with pytest.raises(ValidationError):
        ScientificSearchRequest(source=ScientificSource.CROSSREF)


def test_scientific_search_result_exposes_normalized_fields() -> None:
    result = ScientificSearchResult(
        source=ScientificSource.OPENALEX,
        title="A normalized record",
        authors=["Ada Lovelace"],
        publication_date="2025-01-01",
        url="https://example.org/work",
        language="en",
        document_type="article",
        doi="10.1000/example",
        pmid=None,
        abstract="Summary",
        journal="Journal",
        keyword_used="ai",
    )

    assert result.source == ScientificSource.OPENALEX
    assert result.title == "A normalized record"
    assert result.keyword_used == "ai"
