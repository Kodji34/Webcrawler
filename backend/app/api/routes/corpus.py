from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from backend.app.schemas.corpus import (
    CorpusCreateRequest,
    CorpusCreateResponse,
    CorpusListResponse,
    CorpusRecord,
    CorpusSourceItemsResponse,
)
from backend.app.services.corpus_service import CorpusService

router = APIRouter()
service = CorpusService()


@router.get("/sources", summary="List source texts available for corpus creation")
def list_corpus_sources() -> CorpusSourceItemsResponse:
    return service.list_sources()


@router.post("/create", summary="Create a local corpus from selected imported texts")
def create_corpus(payload: CorpusCreateRequest) -> CorpusCreateResponse:
    try:
        return service.create_corpus(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/items", summary="List local corpora")
def list_corpora() -> CorpusListResponse:
    return service.list_corpora()


@router.get("/items/{corpus_id}", summary="Get a corpus by id")
def get_corpus(corpus_id: str) -> CorpusRecord:
    try:
        return service.get_corpus(corpus_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/items/{corpus_id}/export-text", summary="Export a corpus as plain text")
def export_corpus_text(corpus_id: str) -> PlainTextResponse:
    try:
        return PlainTextResponse(
            service.export_text(corpus_id),
            media_type="text/plain; charset=utf-8",
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
