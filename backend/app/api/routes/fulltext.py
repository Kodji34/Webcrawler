from fastapi import APIRouter, HTTPException

from backend.app.schemas.fulltext import (
    FullTextAcquireImportsRequest,
    FullTextAcquireImportsResponse,
    FullTextItemsResponse,
    FullTextSourceDescriptor,
)
from backend.app.services.fulltext_acquisition_service import FullTextAcquisitionService

router = APIRouter()
service = FullTextAcquisitionService()


@router.get("/sources", summary="List supported authorized full-text sources")
def list_fulltext_sources() -> list[FullTextSourceDescriptor]:
    return service.list_sources()


@router.get("/items", summary="List locally stored full-text acquisition records")
def list_fulltext_items() -> FullTextItemsResponse:
    return service.list_items()


@router.post("/acquire-imports", summary="Attempt authorized full-text acquisition for imported scientific records")
def acquire_fulltext_imports(
    payload: FullTextAcquireImportsRequest,
) -> FullTextAcquireImportsResponse:
    try:
        return service.acquire_imports(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
