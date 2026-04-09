from fastapi import APIRouter, HTTPException

from backend.app.schemas.scientific import (
    ScientificImportSelectionRequest,
    ScientificImportSelectionResponse,
    ScientificImportedRecord,
    ScientificSearchRequest,
    ScientificSearchResponse,
    ScientificSourceDescriptor,
)
from backend.app.services.scientific_search_service import ScientificSearchService

router = APIRouter()
service = ScientificSearchService()


@router.get("/sources", summary="List supported scientific sources")
def list_scientific_sources() -> list[ScientificSourceDescriptor]:
    return service.list_sources()


@router.post("/search", summary="Search a supported scientific source")
def search_scientific_sources(
    payload: ScientificSearchRequest,
) -> ScientificSearchResponse:
    try:
        return service.search(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import-selection", summary="Store selected scientific results locally")
def import_scientific_selection(
    payload: ScientificImportSelectionRequest,
) -> ScientificImportSelectionResponse:
    return service.import_selection(payload)


@router.get("/imports", summary="List locally stored scientific imports")
def list_scientific_imports() -> list[ScientificImportedRecord]:
    return service.list_imported_records()
