from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


class WebImportStatus(StrEnum):
    TEXT_RETRIEVED = "text_retrieved"
    METADATA_ONLY = "metadata_only"
    NOT_AUTHORIZED = "not_authorized"
    FAILED = "failed"


class WebImportEntry(BaseModel):
    url: HttpUrl
    label: str | None = Field(default=None, max_length=180)
    language: str | None = Field(default=None, min_length=2, max_length=16)


class WebImportRequest(BaseModel):
    project_name: str = Field(default="Local Research Project", min_length=1, max_length=120)
    entries: list[WebImportEntry] = Field(min_length=1, max_length=50)


class WebImportedArticle(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid4()))
    project_name: str
    url: str
    label: str | None = None
    title: str | None = None
    description: str | None = None
    language: str | None = None
    source_domain: str | None = None
    status: WebImportStatus
    text_content: str | None = None
    excerpt: str | None = None
    content_type: str | None = None
    imported_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: list[str] = Field(default_factory=list)


class WebImportResponse(BaseModel):
    imported_count: int
    text_retrieved_count: int
    items: list[WebImportedArticle]


class WebImportedItemsResponse(BaseModel):
    items: list[WebImportedArticle]
