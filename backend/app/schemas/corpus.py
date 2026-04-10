from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class CorpusSourceType(StrEnum):
    PDF = "pdf"
    FULLTEXT = "fulltext"
    WEB = "web"


class CorpusSourceItem(BaseModel):
    source_item_id: str
    source_type: CorpusSourceType
    title: str
    source_label: str | None = None
    language: str | None = None
    url: str | None = None
    has_text: bool
    text_excerpt: str | None = None
    notes: list[str] = Field(default_factory=list)


class CorpusStats(BaseModel):
    document_count: int
    word_count: int
    character_count: int
    source_types: dict[str, int] = Field(default_factory=dict)
    languages: dict[str, int] = Field(default_factory=dict)


class CorpusCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=500)
    source_item_ids: list[str] = Field(min_length=1)


class CorpusDocument(BaseModel):
    source_item_id: str
    source_type: CorpusSourceType
    title: str
    language: str | None = None
    url: str | None = None
    text_content: str


class CorpusRecord(BaseModel):
    corpus_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stats: CorpusStats
    documents: list[CorpusDocument]


class CorpusCreateResponse(BaseModel):
    corpus: CorpusRecord


class CorpusListResponse(BaseModel):
    corpora: list[CorpusRecord]


class CorpusSourceItemsResponse(BaseModel):
    items: list[CorpusSourceItem]
