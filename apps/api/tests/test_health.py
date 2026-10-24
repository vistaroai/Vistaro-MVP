"""Tests for liveness (/healthz) and readiness (/readyz) system endpoints."""

from fastapi.testclient import TestClient

from vistaro.core.config import settings
from vistaro.core.middleware import REQUEST_ID_HEADER
from vistaro.main import app, readiness_checkers

client = TestClient(app)


def test_healthz_liveness() -> None:
    """Report that the process is running."""
    response = client.get("/healthz")

    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    assert response.json() == {"status": "ok", "environment": settings.app_env}


def test_readyz_healthy() -> None:
    """Report readiness when both PostgreSQL and Redis dependencies are available."""
    # Ensure real checkers (running with docker compose services) are invoked
    response = client.get("/readyz")

    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    data = response.json()
    assert data["status"] == "ok"
    assert data["environment"] == settings.app_env
    assert data["checks"] == {"database": "ok", "redis": "ok"}


def test_readyz_database_failure() -> None:
    """Report 503 degraded status when database is down, without leaking credentials."""
    original_checker = readiness_checkers["database"]
    readiness_checkers["database"] = lambda: False
    try:
        response = client.get("/readyz")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"] == {"database": "failed", "redis": "ok"}
        # Security: verify no passwords, connection strings, or stack traces leak
        assert "password" not in response.text
        assert "postgresql://" not in response.text
    finally:
        readiness_checkers["database"] = original_checker


def test_readyz_redis_failure() -> None:
    """Report 503 degraded status when Redis is down."""
    original_checker = readiness_checkers["redis"]
    readiness_checkers["redis"] = lambda: False
    try:
        response = client.get("/readyz")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"] == {"database": "ok", "redis": "failed"}
    finally:
        readiness_checkers["redis"] = original_checker


def test_readyz_multiple_failures() -> None:
    """Report 503 degraded status when both dependencies are down."""
    orig_db = readiness_checkers["database"]
    orig_redis = readiness_checkers["redis"]
    readiness_checkers["database"] = lambda: False
    readiness_checkers["redis"] = lambda: False
    try:
        response = client.get("/readyz")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["checks"] == {"database": "failed", "redis": "failed"}
    finally:
        readiness_checkers["database"] = orig_db
        readiness_checkers["redis"] = orig_redis
