from fastapi import APIRouter, HTTPException

from backend.app.schemas.pdf import (
    PDFExtractRequest,
    PDFExtractResponse,
    PDFImportLocalRequest,
    PDFImportResponse,
    PDFImportUrlsRequest,
    PDFItemsResponse,
    PDFJob,
    PDFPreviewRequest,
    PDFPreviewResponse,
    PDFSaveSelectionRequest,
    PDFSaveSelectionResponse,
)
from backend.app.services.pdf_ingestion_service import PDFIngestionService

router = APIRouter()
service = PDFIngestionService()


def _pdf_value_error(exc: ValueError) -> HTTPException:
    detail = str(exc)
    status_code = 404 if detail.startswith("unknown ") else 400
    return HTTPException(status_code=status_code, detail=detail)


@router.post("/import-local", summary="Scan a local folder for PDF files")
def import_local_pdfs(payload: PDFImportLocalRequest) -> PDFImportResponse:
    try:
        return service.import_local(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import-urls", summary="Download direct PDF URLs into the local workspace")
def import_pdf_urls(payload: PDFImportUrlsRequest) -> PDFImportResponse:
    try:
        return service.import_urls(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/extract", summary="Extract text from imported PDF items")
def extract_pdf_text(payload: PDFExtractRequest) -> PDFExtractResponse:
    try:
        return service.extract(payload)
    except ValueError as exc:
        raise _pdf_value_error(exc) from exc


@router.post("/preview", summary="Preview extracted text for a PDF item")
def preview_pdf_text(payload: PDFPreviewRequest) -> PDFPreviewResponse:
    try:
        return service.preview(payload)
    except ValueError as exc:
        raise _pdf_value_error(exc) from exc


@router.post("/save-selection", summary="Save selected processed PDFs into the local project")
def save_pdf_selection(payload: PDFSaveSelectionRequest) -> PDFSaveSelectionResponse:
    try:
        return service.save_selection(payload)
    except ValueError as exc:
        raise _pdf_value_error(exc) from exc


@router.get("/jobs/{job_id}", summary="Read a stored PDF extraction job")
def get_pdf_job(job_id: str) -> PDFJob:
    try:
        return service.get_job(job_id)
    except ValueError as exc:
        raise _pdf_value_error(exc) from exc


@router.get("/items", summary="List imported PDF items and dependency status")
def list_pdf_items() -> PDFItemsResponse:
    return service.list_items()
