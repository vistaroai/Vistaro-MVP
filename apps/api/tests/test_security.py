"""Focused tests for the SEC-001 browser security controls."""

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from vistaro.core.config import Settings, settings
from vistaro.core.security import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    csrf_cookie_options,
    new_csrf_token,
    security_headers,
    session_cookie_options,
)
from vistaro.core.security_middleware import (
    _RATE_LIMIT_SCRIPT,
    CSRFMiddleware,
    RedisRateLimitMiddleware,
)
from vistaro.main import app as api_app


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.fail = False

    async def eval(self, _script: str, _numkeys: int, key: str, _window: int) -> int:
        if self.fail:
            raise ConnectionError("test backend unavailable")
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]


def create_csrf_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(CSRFMiddleware, web_origin="http://localhost:5173")

    @test_app.post("/mutate")
    def mutate() -> dict[str, str]:
        return {"status": "changed"}

    @test_app.get("/read")
    def read() -> dict[str, str]:
        return {"status": "read"}

    return test_app


def create_rate_limit_app(
    store: FakeRedis,
    limit: int = 2,
    window_seconds: int = 60,
) -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(
        RedisRateLimitMiddleware,
        redis_client=store,
        limit=limit,
        window_seconds=window_seconds,
    )

    @test_app.get("/ping")
    def ping() -> dict[str, str]:
        return {"pong": "true"}

    @test_app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return test_app


def test_csrf_rejects_missing_token_and_origin() -> None:
    client = TestClient(create_csrf_app())
    client.cookies.set(CSRF_COOKIE_NAME, "same-token")

    missing = client.post("/mutate", headers={"Origin": "http://localhost:5173"})
    wrong_origin = client.post(
        "/mutate",
        headers={
            "Origin": "https://attacker.example",
            CSRF_HEADER_NAME: "same-token",
        },
    )

    assert missing.status_code == 403
    assert missing.json()["error"]["code"] == "CSRF_VALIDATION_FAILED"
    assert wrong_origin.status_code == 403


def test_csrf_accepts_matching_token_from_configured_origin() -> None:
    client = TestClient(create_csrf_app())
    client.cookies.set(CSRF_COOKIE_NAME, "token-123")
    response = client.post(
        "/mutate",
        headers={"Origin": "http://LOCALHOST:5173", CSRF_HEADER_NAME: "token-123"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "changed"}


def test_csrf_rejects_mismatched_token_and_allows_safe_requests() -> None:
    client = TestClient(create_csrf_app())
    client.cookies.set(CSRF_COOKIE_NAME, "cookie")
    mismatch = client.post(
        "/mutate",
        headers={"Origin": "http://localhost:5173", CSRF_HEADER_NAME: "header"},
    )

    assert mismatch.status_code == 403
    assert client.get("/read").status_code == 200


def test_cookie_defaults_are_environment_aware() -> None:
    local_session = session_cookie_options("local")
    production_session = session_cookie_options("production")
    local_csrf = csrf_cookie_options("local")
    production_csrf = csrf_cookie_options("staging")

    assert local_session == {
        "httponly": True,
        "secure": False,
        "samesite": "lax",
        "path": "/",
    }
    assert production_session["httponly"] is True
    assert production_session["secure"] is True
    assert production_session["samesite"] == "none"
    assert local_csrf["httponly"] is False
    assert local_csrf["secure"] is False
    assert production_csrf["secure"] is True
    assert production_csrf["samesite"] == "none"


def test_csrf_token_is_unpredictable() -> None:
    assert new_csrf_token() != new_csrf_token()


def test_security_headers_cover_success_and_error_responses() -> None:
    with TestClient(api_app) as client:
        success = client.get("/healthz")
        error = client.get("/not-a-route")
        docs = client.get("/docs")
    assert success.status_code == 200
    assert error.status_code == 404
    assert error.json()["error"]["code"] == "NOT_FOUND"
    assert docs.status_code == 200
    assert "swagger-ui-bundle.js" in docs.text
    for response in (success, error, docs):
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "default-src 'none'" in response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
        assert "Strict-Transport-Security" not in response.headers


def test_cors_remains_limited_to_the_configured_web_origin() -> None:
    with TestClient(api_app) as client:
        allowed = client.get("/healthz", headers={"Origin": settings.web_origin})
        denied = client.get("/healthz", headers={"Origin": "https://attacker.example"})

    assert allowed.headers["Access-Control-Allow-Origin"] == settings.web_origin
    assert allowed.headers["Access-Control-Allow-Credentials"] == "true"
    assert "Access-Control-Allow-Origin" not in denied.headers


def test_security_headers_add_hsts_only_outside_local_development() -> None:
    assert "Strict-Transport-Security" not in security_headers("local")
    assert "Strict-Transport-Security" not in security_headers("test")
    assert security_headers("production")["Strict-Transport-Security"] == (
        "max-age=31536000; includeSubDomains"
    )


def test_csrf_endpoint_sets_readable_short_lived_token_cookie() -> None:
    with TestClient(api_app) as client:
        response = client.get("/csrf", headers={"Origin": settings.web_origin})
    cookie = response.headers["Set-Cookie"].lower()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Access-Control-Allow-Origin"] == settings.web_origin
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert f"csrf_token={response.json()['csrf_token']}".lower() in cookie
    assert "httponly" not in cookie
    assert "samesite=lax" in cookie
    assert "max-age=3600" in cookie


def test_rate_limit_threshold_forwarded_ip_and_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    now = [120.0]
    monkeypatch.setattr("vistaro.core.security_middleware.time.time", lambda: now[0])
    store = FakeRedis()
    client = TestClient(create_rate_limit_app(store, limit=2, window_seconds=60))

    first = client.get("/ping", headers={"X-Forwarded-For": "203.0.113.1"})
    second = client.get("/ping", headers={"X-Forwarded-For": "203.0.113.2"})
    limited = client.get("/ping", headers={"X-Forwarded-For": "203.0.113.3"})

    assert first.status_code == second.status_code == 200
    assert first.headers["X-RateLimit-Remaining"] == "1"
    assert second.headers["X-RateLimit-Remaining"] == "0"
    assert limited.status_code == 429
    assert limited.headers["Retry-After"]
    assert limited.json()["error"]["code"] == "RATE_LIMITED"
    assert len(store.counts) == 1  # forwarded values did not change the client identity

    now[0] += 60
    reset = client.get("/ping")
    assert reset.status_code == 200
    assert reset.headers["X-RateLimit-Remaining"] == "1"


def test_rate_limit_fails_closed_but_does_not_block_health() -> None:
    store = FakeRedis()
    store.fail = True
    client = TestClient(create_rate_limit_app(store))

    assert client.get("/healthz").status_code == 200
    unavailable = client.get("/ping")
    assert unavailable.status_code == 503
    assert unavailable.json()["error"]["code"] == "SERVICE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_redis_rate_limit_script_increments_and_expires() -> None:
    client = Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
    try:
        await client.ping()
    except RedisError:
        await client.aclose()
        pytest.skip("Redis service is not available")

    key = f"vistaro:test:sec001:{uuid.uuid4().hex}"
    try:
        first = await client.eval(_RATE_LIMIT_SCRIPT, 1, key, 60)
        second = await client.eval(_RATE_LIMIT_SCRIPT, 1, key, 60)
        ttl = await client.ttl(key)
        assert first == 1
        assert second == 2
        assert 0 < ttl <= 60
    finally:
        await client.delete(key)
        await client.aclose()


@pytest.mark.parametrize(
    "setting",
    ["rate_limit_requests", "rate_limit_window_seconds"],
)
def test_rate_limit_configuration_must_be_positive(setting: str) -> None:
    with pytest.raises(ValidationError):
        Settings(**{setting: 0})


