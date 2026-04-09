from worker.app.celery_app import celery_app


def test_celery_app_uses_redis_defaults() -> None:
    assert celery_app.conf.broker_url.startswith("redis://")
    assert celery_app.conf.result_backend.startswith("redis://")
    assert celery_app.conf.task_default_queue == "research-default"
