from fastapi import APIRouter

from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/health", summary="Phase 1 health and stack metadata")
def healthcheck() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
        "phase": {
            "number": 1,
            "name": "Phase 1 Foundation",
            "focus": "Project bootstrap, navigation shell, and local stack wiring",
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
            "research-queue",
            "collections",
            "schedules",
            "settings",
        ],
    }
