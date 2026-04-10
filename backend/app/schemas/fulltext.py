from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class FullTextSource(StrEnum):
    EUROPE_PMC = "europe_pmc"
    ELSEVIER = "elsevier_tdm"
    HAL = "hal"
    OPENEDITION = "openedition"
    CAIRN = "cairn"
    ERUDIT = "erudit"


class FullTextOutcome(StrEnum):
    FULL_TEXT_RETRIEVED = "full_text_retrieved"
    FULL_TEXT_NOT_AUTHORIZED = "full_text_not_authorized"
    METADATA_ONLY = "metadata_only"
    FAILED = "failed"


class FullTextAccessMode(StrEnum):
    OPEN_ACCESS = "open_access"
    AUTHENTICATED_API = "authenticated_api"
    BIBLIOGRAPHIC_ONLY = "bibliographic_only"
    NOT_AUTHORIZED = "not_authorized"
    UNKNOWN = "unknown"


class FullTextSourceDescriptor(BaseModel):
    key: FullTextSource
    label: str
    description: str
    official_url: str
    requires_authentication: bool
    supports_full_text: bool
    notes: str


class FullTextAcquireImportsRequest(BaseModel):
    import_ids: list[str] = Field(min_length=1)


class FullTextAcquisitionItem(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid4()))
    scientific_import_id: str
    source: FullTextSource
    outcome: FullTextOutcome
    access_mode: FullTextAccessMode
    title: str
    doi: str | None = None
    pmid: str | None = None
    landing_url: str
    full_text_url: str | None = None
    license_name: str | None = None
    language: str | None = None
    journal: str | None = None
    text_content: str | None = None
    excerpt: str | None = None
    notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FullTextAcquireImportsResponse(BaseModel):
    requested_count: int
    acquired_count: int
    items: list[FullTextAcquisitionItem]


class FullTextItemsResponse(BaseModel):
    items: list[FullTextAcquisitionItem]
