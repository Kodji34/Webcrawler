from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_endpoint_exposes_phase_one_metadata() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["phase"]["number"] == 1
    assert set(payload["i18n"]["languages"]) == {"en", "fr"}
    assert payload["services"]["celery_queue"] == "research-default"
