from fastapi import APIRouter

from backend.app.schemas.web import (
    WebImportedItemsResponse,
    WebImportRequest,
    WebImportResponse,
)
from backend.app.services.web_import_service import WebImportService

router = APIRouter()
service = WebImportService()


@router.post("/import-urls", summary="Import public web article URLs without bypassing access controls")
def import_web_urls(payload: WebImportRequest) -> WebImportResponse:
    return service.import_urls(payload)


@router.get("/items", summary="List locally imported web articles")
def list_web_items() -> WebImportedItemsResponse:
    return service.list_items()
