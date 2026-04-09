from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.connectors.pdf.local_files import LocalPDFConnector
from backend.app.connectors.pdf.remote_pdf import RemotePDFConnector
from backend.app.core.config import get_settings
from backend.app.schemas.pdf import (
    PDFDependencyStatus,
    PDFExtractRequest,
    PDFExtractResponse,
    PDFExtractionStatus,
    PDFImportLocalRequest,
    PDFImportResponse,
    PDFImportUrlsRequest,
    PDFItem,
    PDFItemsResponse,
    PDFJob,
    PDFPreviewRequest,
    PDFPreviewResponse,
    PDFSaveSelectionRequest,
    PDFSaveSelectionResponse,
    PDFSavedRecord,
)
from backend.app.services.pdf_extraction_service import PDFExtractionService


class PDFPersistenceStore:
    def __init__(self, store_path: str | None = None) -> None:
        settings = get_settings()
        self.path = Path(store_path or settings.pdf_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _ensure_store(self) -> None:
        if not self.path.exists():
            self.path.write_text(
                json.dumps({"items": [], "saved_records": [], "jobs": []}, indent=2),
                encoding="utf-8",
            )

    def _load(self) -> dict[str, Any]:
        self._ensure_store()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_items(self) -> list[PDFItem]:
        payload = self._load()
        return [PDFItem.model_validate(item) for item in payload.get("items", [])]

    def upsert_items(self, items: list[PDFItem]) -> None:
        with self._lock:
            payload = self._load()
            existing = {item["id"]: item for item in payload.get("items", [])}
            for item in items:
                existing[item.id] = item.model_dump(mode="json")
            payload["items"] = list(existing.values())
            self._save(payload)

    def get_item(self, item_id: str) -> PDFItem | None:
        for item in self.list_items():
            if item.id == item_id:
                return item
        return None

    def list_jobs(self) -> list[PDFJob]:
        payload = self._load()
        return [PDFJob.model_validate(job) for job in payload.get("jobs", [])]

    def upsert_job(self, job: PDFJob) -> None:
        with self._lock:
            payload = self._load()
            existing = {entry["job_id"]: entry for entry in payload.get("jobs", [])}
            existing[job.job_id] = job.model_dump(mode="json")
            payload["jobs"] = list(existing.values())
            self._save(payload)

    def get_job(self, job_id: str) -> PDFJob | None:
        for job in self.list_jobs():
            if job.job_id == job_id:
                return job
        return None

    def append_saved_records(self, records: list[PDFSavedRecord]) -> None:
        with self._lock:
            payload = self._load()
            payload["saved_records"].extend(
                record.model_dump(mode="json") for record in records
            )
            self._save(payload)


class PDFIngestionService:
    def __init__(
        self,
        *,
        store: PDFPersistenceStore | None = None,
        extraction_service: PDFExtractionService | None = None,
    ) -> None:
        self.settings = get_settings()
        self.store = store or PDFPersistenceStore()
        self.local_connector = LocalPDFConnector()
        self.remote_connector = RemotePDFConnector()
        self.extraction_service = extraction_service or PDFExtractionService()
        self.download_dir = Path(self.settings.pdf_download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def dependency_status(self) -> PDFDependencyStatus:
        return self.extraction_service.dependency_status()

    def list_items(self) -> PDFItemsResponse:
        items = sorted(
            self.store.list_items(),
            key=lambda item: item.created_at,
            reverse=True,
        )
        return PDFItemsResponse(items=items, dependency_status=self.dependency_status())

    def import_local(self, request: PDFImportLocalRequest) -> PDFImportResponse:
        candidates = self.local_connector.import_items(
            request.directory_path,
            recursive=request.recursive,
            language=request.language,
        )
        items = [self._build_item(candidate) for candidate in candidates]
        self.store.upsert_items(items)
        return PDFImportResponse(imported_count=len(items), items=items)

    def import_urls(self, request: PDFImportUrlsRequest) -> PDFImportResponse:
        candidates = self.remote_connector.import_items(
            request.entries,
            cache_dir=self.download_dir,
            import_type=request.import_type,
            language=request.language,
        )
        items = [self._build_item(candidate) for candidate in candidates]
        self.store.upsert_items(items)
        return PDFImportResponse(imported_count=len(items), items=items)

    def preview(self, request: PDFPreviewRequest) -> PDFPreviewResponse:
        item = self._require_item(request.item_id)
        processed = self._process_item(
            item,
            language=request.language,
            extraction_mode=request.extraction_mode,
            cleaning_options=request.cleaning_options,
        )
        self.store.upsert_items([processed])
        return PDFPreviewResponse(
            item=processed,
            dependency_status=self.dependency_status(),
        )

    def extract(self, request: PDFExtractRequest) -> PDFExtractResponse:
        job = PDFJob(
            item_ids=request.item_ids,
            extraction_mode=request.extraction_mode,
            status=PDFExtractionStatus.READY,
        )
        processed_items: list[PDFItem] = []
        warnings: list[str] = []
        statuses: list[PDFExtractionStatus] = []

        for item_id in request.item_ids:
            item = self._require_item(item_id)
            processed = self._process_item(
                item,
                language=request.language,
                extraction_mode=request.extraction_mode,
                cleaning_options=request.cleaning_options,
            )
            processed_items.append(processed)
            warnings.extend(processed.dependency_messages)
            warnings.extend(processed.heuristic_notes)
            statuses.append(processed.extraction_status)

        job.processed_count = len(processed_items)
        job.warnings = list(dict.fromkeys(warnings))
        job.completed_at = datetime.now(UTC)
        if any(status == PDFExtractionStatus.FAILED for status in statuses):
            job.status = PDFExtractionStatus.FAILED
        elif any(status == PDFExtractionStatus.DEPENDENCY_MISSING for status in statuses):
            job.status = PDFExtractionStatus.DEPENDENCY_MISSING
        else:
            job.status = PDFExtractionStatus.READY

        self.store.upsert_items(processed_items)
        self.store.upsert_job(job)
        return PDFExtractResponse(
            job=job,
            items=processed_items,
            dependency_status=self.dependency_status(),
        )

    def save_selection(self, request: PDFSaveSelectionRequest) -> PDFSaveSelectionResponse:
        selected_items = [self._require_item(item_id) for item_id in request.item_ids]
        updated_items: list[PDFItem] = []
        records: list[PDFSavedRecord] = []
        for item in selected_items:
            if not item.text_raw and not item.text_cleaned:
                raise ValueError(f"pdf item must be previewed or extracted before save: {item.id}")
            updated = item.model_copy(
                update={
                    "saved_to_project": True,
                    "project_name": request.project_name,
                    "extraction_status": PDFExtractionStatus.SAVED,
                }
            )
            updated_items.append(updated)
            records.append(PDFSavedRecord(project_name=request.project_name, item=updated))

        self.store.upsert_items(updated_items)
        self.store.append_saved_records(records)
        return PDFSaveSelectionResponse(
            project_name=request.project_name,
            saved_count=len(records),
            records=records,
        )

    def get_job(self, job_id: str) -> PDFJob:
        job = self.store.get_job(job_id)
        if not job:
            raise ValueError(f"unknown job: {job_id}")
        return job

    def _build_item(self, candidate: Any) -> PDFItem:
        page_count, title, author = self.extraction_service.inspect_pdf(candidate.storage_path)
        existing = self._find_existing(candidate.original_path, candidate.original_url)
        base_item = existing or PDFItem(
            source=candidate.source,
            file_name=candidate.file_name,
            original_path=candidate.original_path,
            original_url=candidate.original_url,
            storage_path=str(candidate.storage_path),
            import_type=candidate.import_type,
            language=candidate.language,
            linked_record_title=candidate.linked_record_title,
        )
        return base_item.model_copy(
            update={
                "source": candidate.source,
                "file_name": candidate.file_name,
                "original_path": candidate.original_path,
                "original_url": candidate.original_url,
                "storage_path": str(candidate.storage_path),
                "import_type": candidate.import_type,
                "language": candidate.language,
                "page_count": page_count,
                "title": title or base_item.title,
                "author": author or base_item.author,
                "linked_record_title": candidate.linked_record_title,
            }
        )

    def _find_existing(
        self,
        original_path: str | None,
        original_url: str | None,
    ) -> PDFItem | None:
        for item in self.store.list_items():
            if original_path and item.original_path == original_path:
                return item
            if original_url and str(item.original_url or "") == original_url:
                return item
        return None

    def _require_item(self, item_id: str) -> PDFItem:
        item = self.store.get_item(item_id)
        if not item:
            raise ValueError(f"unknown pdf item: {item_id}")
        return item

    def _process_item(
        self,
        item: PDFItem,
        *,
        language: str | None,
        extraction_mode,
        cleaning_options,
    ) -> PDFItem:
        path = Path(item.storage_path)
        if not path.exists():
            return item.model_copy(
                update={
                    "extraction_status": PDFExtractionStatus.FAILED,
                    "dependency_messages": [f"stored PDF is missing: {path}"],
                }
            )

        processed = self.extraction_service.process_pdf(
            path,
            requested_mode=extraction_mode,
            language=language or item.language,
            cleaning_options=cleaning_options,
        )
        return item.model_copy(
            update={
                "page_count": processed.page_count or item.page_count,
                "title": processed.title or item.title,
                "author": processed.author or item.author,
                "language": language or item.language,
                "extraction_mode": extraction_mode,
                "used_extraction_mode": processed.used_mode,
                "extraction_status": processed.status,
                "text_raw": processed.raw_text,
                "text_cleaned": processed.cleaned_text,
                "has_ocr": processed.has_ocr,
                "ocr_recommended": processed.ocr_recommended,
                "dependency_messages": processed.dependency_messages,
                "heuristic_notes": processed.heuristic_notes,
                "preview_excerpt": processed.preview_excerpt,
            }
        )
