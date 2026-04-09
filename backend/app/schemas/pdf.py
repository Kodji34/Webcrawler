from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Self
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, model_validator


class PDFSource(StrEnum):
    LOCAL_FILES = "local_files"
    REMOTE_PDF = "remote_pdf"
    LINKED_SCIENTIFIC_RESULT = "linked_scientific_result"


class PDFImportType(StrEnum):
    LOCAL = "local"
    REMOTE = "remote"
    LINKED_SCIENTIFIC_RESULT = "linked_scientific_result"


class PDFExtractionMode(StrEnum):
    NATIVE = "native"
    OCR = "ocr"
    AUTO = "auto"


class PDFExtractionStatus(StrEnum):
    IMPORTED = "imported"
    READY = "ready"
    SAVED = "saved"
    FAILED = "failed"
    DEPENDENCY_MISSING = "dependency_missing"


class PDFCleaningOptions(BaseModel):
    generate_cleaned_text: bool = False
    remove_headers: bool = False
    remove_footers: bool = False
    remove_page_numbers: bool = False
    remove_bibliography: bool = False
    normalize_whitespace: bool = False


class PDFItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: PDFSource
    file_name: str
    original_path: str | None = None
    original_url: HttpUrl | None = None
    storage_path: str
    import_type: PDFImportType
    language: str | None = None
    extraction_mode: PDFExtractionMode = PDFExtractionMode.AUTO
    used_extraction_mode: PDFExtractionMode | None = None
    extraction_status: PDFExtractionStatus = PDFExtractionStatus.IMPORTED
    page_count: int | None = None
    title: str | None = None
    author: str | None = None
    text_raw: str | None = None
    text_cleaned: str | None = None
    has_ocr: bool = False
    ocr_recommended: bool = False
    dependency_messages: list[str] = Field(default_factory=list)
    heuristic_notes: list[str] = Field(default_factory=list)
    linked_record_title: str | None = None
    saved_to_project: bool = False
    project_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    preview_excerpt: str | None = None


class PDFImportLocalRequest(BaseModel):
    directory_path: str = Field(min_length=1, max_length=500)
    recursive: bool = True
    language: str | None = Field(default=None, min_length=2, max_length=16)


class PDFImportUrlEntry(BaseModel):
    url: HttpUrl
    label: str | None = Field(default=None, max_length=240)
    linked_record_title: str | None = Field(default=None, max_length=240)


class PDFImportUrlsRequest(BaseModel):
    entries: list[PDFImportUrlEntry] = Field(min_length=1)
    import_type: PDFImportType = PDFImportType.REMOTE
    language: str | None = Field(default=None, min_length=2, max_length=16)

    @model_validator(mode="after")
    def validate_import_type(self) -> Self:
        if self.import_type == PDFImportType.LOCAL:
            raise ValueError("import_type local is not valid for URL imports")
        return self


class PDFImportResponse(BaseModel):
    imported_count: int
    items: list[PDFItem]


class PDFDependencyStatus(BaseModel):
    pymupdf_available: bool
    pdfplumber_available: bool
    pytesseract_available: bool
    tesseract_available: bool
    ocrmypdf_available: bool
    messages: list[str] = Field(default_factory=list)


class PDFExtractRequest(BaseModel):
    item_ids: list[str] = Field(min_length=1)
    extraction_mode: PDFExtractionMode = PDFExtractionMode.AUTO
    language: str | None = Field(default=None, min_length=2, max_length=16)
    cleaning_options: PDFCleaningOptions = Field(default_factory=PDFCleaningOptions)


class PDFPreviewRequest(BaseModel):
    item_id: str
    extraction_mode: PDFExtractionMode = PDFExtractionMode.AUTO
    language: str | None = Field(default=None, min_length=2, max_length=16)
    cleaning_options: PDFCleaningOptions = Field(default_factory=PDFCleaningOptions)


class PDFJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    item_ids: list[str]
    extraction_mode: PDFExtractionMode
    status: PDFExtractionStatus
    processed_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class PDFPreviewResponse(BaseModel):
    item: PDFItem
    dependency_status: PDFDependencyStatus


class PDFExtractResponse(BaseModel):
    job: PDFJob
    items: list[PDFItem]
    dependency_status: PDFDependencyStatus


class PDFSaveSelectionRequest(BaseModel):
    project_name: str = Field(default="Local Research Project", min_length=1, max_length=120)
    item_ids: list[str] = Field(min_length=1)


class PDFSavedRecord(BaseModel):
    save_id: str = Field(default_factory=lambda: str(uuid4()))
    project_name: str
    saved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    item: PDFItem


class PDFSaveSelectionResponse(BaseModel):
    project_name: str
    saved_count: int
    records: list[PDFSavedRecord]


class PDFItemsResponse(BaseModel):
    items: list[PDFItem]
    dependency_status: PDFDependencyStatus
