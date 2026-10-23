"""Smoke tests for the bootstrap API."""

from fastapi.testclient import TestClient

from vistaro.main import app

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "local"}
