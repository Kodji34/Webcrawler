from fastapi import APIRouter

from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/health", summary="Phase 2 health and scientific stack metadata")
def healthcheck() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
        "phase": {
            "number": 2,
            "name": "Phase 2 Scientific Connectors",
            "focus": "Scientific source connectors, normalized metadata search, and local import flows",
        },
        "i18n": {"languages": ["en", "fr"], "default_language": "en"},
        "services": {
            "api": settings.backend_url,
            "frontend": settings.frontend_url,
            "postgres": settings.postgres_url,
            "redis": settings.redis_url,
            "celery_broker": settings.celery_broker_url,
            "celery_queue": settings.celery_default_queue,
        },
        "screens": [
            "dashboard",
            "scientific-search",
            "research-queue",
            "collections",
            "schedules",
            "settings",
        ],
    }
