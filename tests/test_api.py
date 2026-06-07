import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from eda_log_ai.api import app


def test_api_health_and_analyze():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    homepage = client.get("/")
    assert homepage.status_code == 200
    assert "EDA Log AI Workbench" in homepage.text

    config = client.get("/config")
    assert config.status_code == 200
    assert config.json()["default_model"] == "qwen3-max"

    response = client.post(
        "/analyze",
        json={"log_text": "[ERROR] License checkout failed: feature CALIBRE_DRC not found", "use_llm": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["categories"][0]["id"] == "license_environment"
    assert body["recommendations"]
