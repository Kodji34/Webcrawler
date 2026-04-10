from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.connectors.fulltext import (
    CairnConnector,
    ElsevierTdmConnector,
    EruditConnector,
    EuropePmcConnector,
    HalFullTextConnector,
    OpenEditionConnector,
)
from backend.app.core.config import get_settings
from backend.app.schemas.fulltext import (
    FullTextAccessMode,
    FullTextAcquireImportsRequest,
    FullTextAcquireImportsResponse,
    FullTextAcquisitionItem,
    FullTextItemsResponse,
    FullTextOutcome,
    FullTextSourceDescriptor,
)
from backend.app.services.scientific_search_service import ScientificSearchService


class FullTextPersistenceStore:
    def __init__(self, store_path: str | None = None) -> None:
        settings = get_settings()
        self.path = Path(store_path or settings.fulltext_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _ensure_store(self) -> None:
        if not self.path.exists():
            self.path.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        self._ensure_store()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def append_items(self, items: list[FullTextAcquisitionItem]) -> None:
        with self._lock:
            payload = self._load()
            payload["items"].extend(item.model_dump(mode="json") for item in items)
            self._save(payload)

    def list_items(self) -> list[FullTextAcquisitionItem]:
        payload = self._load()
        return [FullTextAcquisitionItem.model_validate(item) for item in payload.get("items", [])]


class FullTextAcquisitionService:
    def __init__(
        self,
        *,
        store: FullTextPersistenceStore | None = None,
        scientific_service: ScientificSearchService | None = None,
    ) -> None:
        self.store = store or FullTextPersistenceStore()
        self.scientific_service = scientific_service or ScientificSearchService()
        self.connectors = [
            HalFullTextConnector(),
            OpenEditionConnector(),
            CairnConnector(),
            EruditConnector(),
            ElsevierTdmConnector(),
            EuropePmcConnector(),
        ]

    def list_sources(self) -> list[FullTextSourceDescriptor]:
        return [connector.describe() for connector in self.connectors]

    def list_items(self) -> FullTextItemsResponse:
        return FullTextItemsResponse(items=self.store.list_items())

    def acquire_imports(
        self,
        request: FullTextAcquireImportsRequest,
    ) -> FullTextAcquireImportsResponse:
        records_by_id = {
            record.import_id: record for record in self.scientific_service.list_imported_records()
        }
        items: list[FullTextAcquisitionItem] = []
        for import_id in request.import_ids:
            record = records_by_id.get(import_id)
            if record is None:
                items.append(
                    FullTextAcquisitionItem(
                        scientific_import_id=import_id,
                        source=self.connectors[-1].source,
                        outcome=FullTextOutcome.FAILED,
                        access_mode=FullTextAccessMode.UNKNOWN,
                        title="Unknown scientific import",
                        landing_url="",
                        notes=["The referenced scientific import does not exist in local storage."],
                    )
                )
                continue

            items.append(self._acquire_for_record(record))

        self.store.append_items(items)
        return FullTextAcquireImportsResponse(
            requested_count=len(request.import_ids),
            acquired_count=sum(
                1 for item in items if item.outcome == FullTextOutcome.FULL_TEXT_RETRIEVED
            ),
            items=items,
        )

    def _acquire_for_record(self, record):
        connector = next((item for item in self.connectors if item.supports(record)), None)
        if connector is None:
            return FullTextAcquisitionItem(
                scientific_import_id=record.import_id,
                source=self.connectors[-1].source,
                outcome=FullTextOutcome.METADATA_ONLY,
                access_mode=FullTextAccessMode.UNKNOWN,
                title=record.title,
                doi=record.doi,
                pmid=record.pmid,
                landing_url=record.url,
                journal=record.journal,
                language=record.metadata.language,
                notes=["No authorized full-text connector matched this imported record. Metadata stays available."],
            )

        return connector.acquire(record)
