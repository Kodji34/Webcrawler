from datetime import UTC, datetime

from worker.app.celery_app import celery_app


@celery_app.task(name="worker.tasks.heartbeat")
def heartbeat() -> dict[str, str]:
    return {
        "status": "ready",
        "message": "Phase 1 worker heartbeat task is registered.",
        "timestamp": datetime.now(UTC).isoformat(),
    }
