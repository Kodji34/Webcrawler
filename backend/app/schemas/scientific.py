from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Self
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class ScientificSource(StrEnum):
    CROSSREF = "crossref"
    OPENALEX = "openalex"
    PUBMED = "pubmed"
    HAL = "hal"


class IdentifierType(StrEnum):
    DOI = "doi"
    PMID = "pmid"
    HAL_ID = "hal_id"


class ScientificSearchRequest(BaseModel):
    source: ScientificSource
    query: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    max_results: int = Field(default=10, ge=1, le=50)
    language: str | None = Field(default=None, min_length=2, max_length=16)
    identifier: str | None = None
    identifier_type: IdentifierType | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> Self:
        if not self.query and not self.identifier:
            raise ValueError("query or identifier must be provided")

        if self.identifier and not self.identifier_type:
            raise ValueError("identifier_type is required when identifier is provided")

        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")

        return self


class ScientificSearchResult(BaseModel):
    source: ScientificSource
    title: str
    authors: list[str] = Field(default_factory=list)
    publication_date: str | None = None
    url: str
    language: str | None = None
    document_type: str | None = None
    doi: str | None = None
    pmid: str | None = None
    abstract: str | None = None
    journal: str | None = None
    pdf_url: str | None = None
    keyword_used: str


class ScientificSourceDescriptor(BaseModel):
    key: ScientificSource
    label: str
    description: str
    official_api_url: str
    supports_date_range: bool
    supports_language: bool
    supported_identifiers: list[IdentifierType] = Field(default_factory=list)
    max_results_limit: int = 50


class ScientificSearchResponse(BaseModel):
    query_log_id: str
    source: ScientificSource
    results: list[ScientificSearchResult]
    total_results: int


class ScientificImportSelectionRequest(BaseModel):
    project_name: str = Field(default="Local Research Project", min_length=1, max_length=120)
    results: list[ScientificSearchResult] = Field(min_length=1)


class ScientificImportedRecord(BaseModel):
    import_id: str = Field(default_factory=lambda: str(uuid4()))
    project_name: str
    imported_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: ScientificSource
    title: str
    doi: str | None = None
    pmid: str | None = None
    publication_date: str | None = None
    journal: str | None = None
    url: str
    keyword_used: str
    metadata: ScientificSearchResult


class ScientificImportSelectionResponse(BaseModel):
    project_name: str
    imported_count: int
    records: list[ScientificImportedRecord]


class ScientificQueryLogRecord(BaseModel):
    query_log_id: str = Field(default_factory=lambda: str(uuid4()))
    launched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: ScientificSource
    query: str | None = None
    identifier: str | None = None
    identifier_type: IdentifierType | None = None
    language: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    max_results: int
    result_count: int
