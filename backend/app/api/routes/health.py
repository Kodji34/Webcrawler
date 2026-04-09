from fastapi import APIRouter

from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/health", summary="Phase 3 health and PDF/scientific stack metadata")
def healthcheck() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
        "phase": {
            "number": 3,
            "name": "Phase 3 PDF OCR Pipeline",
            "focus": "Scientific connectors, PDF ingestion, native extraction, OCR preview, and local project saves",
        },
        "i18n": {"languages": ["en", "fr"], "default_language": "en"},
        "services": {
            "api": settings.backend_url,
            "frontend": settings.frontend_url,
            "postgres": settings.postgres_url,
            "redis": settings.redis_url,
            "celery_broker": settings.celery_broker_url,
            "celery_queue": settings.celery_default_queue,
            "pdf_store": settings.pdf_store_path,
            "pdf_cache": settings.pdf_download_dir,
        },
        "screens": [
            "dashboard",
            "scientific-search",
            "pdf-workspace",
            "research-queue",
            "collections",
            "schedules",
            "settings",
        ],
    }
