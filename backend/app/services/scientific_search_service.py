from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.connectors.scientific.crossref import CrossrefConnector
from backend.app.connectors.scientific.hal import HalConnector
from backend.app.connectors.scientific.openalex import OpenAlexConnector
from backend.app.connectors.scientific.pubmed import PubMedConnector
from backend.app.core.config import get_settings
from backend.app.schemas.scientific import (
    ScientificImportSelectionRequest,
    ScientificImportSelectionResponse,
    ScientificImportedRecord,
    ScientificQueryLogRecord,
    ScientificSearchRequest,
    ScientificSearchResponse,
    ScientificSource,
    ScientificSourceDescriptor,
)


class ScientificPersistenceStore:
    def __init__(self, store_path: str | None = None) -> None:
        settings = get_settings()
        self.path = Path(store_path or settings.scientific_store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _ensure_store(self) -> None:
        if not self.path.exists():
            self.path.write_text(
                json.dumps({"queries": [], "imports": []}, indent=2),
                encoding="utf-8",
            )

    def _load(self) -> dict[str, Any]:
        self._ensure_store()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def append_query(self, record: ScientificQueryLogRecord) -> None:
        with self._lock:
            payload = self._load()
            payload["queries"].append(record.model_dump(mode="json"))
            self._save(payload)

    def append_imports(self, records: list[ScientificImportedRecord]) -> None:
        with self._lock:
            payload = self._load()
            payload["imports"].extend(record.model_dump(mode="json") for record in records)
            self._save(payload)

    def list_imports(self) -> list[ScientificImportedRecord]:
        payload = self._load()
        return [
            ScientificImportedRecord.model_validate(record)
            for record in payload.get("imports", [])
        ]


class ScientificSearchService:
    def __init__(self, store: ScientificPersistenceStore | None = None) -> None:
        self.store = store or ScientificPersistenceStore()
        self.connectors = {
            ScientificSource.CROSSREF: CrossrefConnector(),
            ScientificSource.OPENALEX: OpenAlexConnector(),
            ScientificSource.PUBMED: PubMedConnector(),
            ScientificSource.HAL: HalConnector(),
        }

    def list_sources(self) -> list[ScientificSourceDescriptor]:
        return [connector.describe() for connector in self.connectors.values()]

    def search(self, request: ScientificSearchRequest) -> ScientificSearchResponse:
        connector = self.connectors[request.source]
        if (
            request.identifier_type
            and request.identifier_type not in connector.describe().supported_identifiers
        ):
            raise ValueError(
                f"{request.source.value} does not support identifier type {request.identifier_type.value}"
            )
        results = connector.search(request)
        query_record = ScientificQueryLogRecord(
            source=request.source,
            query=request.query,
            identifier=request.identifier,
            identifier_type=request.identifier_type,
            language=request.language,
            start_date=request.start_date,
            end_date=request.end_date,
            max_results=request.max_results,
            result_count=len(results),
        )
        self.store.append_query(query_record)
        return ScientificSearchResponse(
            query_log_id=query_record.query_log_id,
            source=request.source,
            results=results,
            total_results=len(results),
        )

    def import_selection(
        self,
        request: ScientificImportSelectionRequest,
    ) -> ScientificImportSelectionResponse:
        records = [
            ScientificImportedRecord(
                project_name=request.project_name,
                source=result.source,
                title=result.title,
                doi=result.doi,
                pmid=result.pmid,
                publication_date=result.publication_date,
                journal=result.journal,
                url=result.url,
                keyword_used=result.keyword_used,
                metadata=result,
            )
            for result in request.results
        ]
        self.store.append_imports(records)
        return ScientificImportSelectionResponse(
            project_name=request.project_name,
            imported_count=len(records),
            records=records,
        )

    def list_imported_records(self) -> list[ScientificImportedRecord]:
        return self.store.list_imports()
