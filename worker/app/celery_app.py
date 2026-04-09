from celery import Celery

from backend.app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pycrawler-worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_default_queue=settings.celery_default_queue,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["worker.app.tasks"])
