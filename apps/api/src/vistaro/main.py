"""FastAPI application entry point."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy import text

from vistaro.api.auth import router as auth_router
from vistaro.api.deps import rebind_session_csrf
from vistaro.core.config import settings
from vistaro.core.errors import ErrorEnvelope, register_error_handlers
from vistaro.core.middleware import RequestIDMiddleware
from vistaro.core.security import csrf_cookie_options, new_csrf_token
from vistaro.core.security_middleware import (
    CSRFMiddleware,
    RedisRateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from vistaro.db.tenancy import build_engine


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Close the shared Redis rate-limit client when the API shuts down."""
    application.state.rate_limit_redis = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=2.0,
        socket_timeout=2.0,
    )
    try:
        yield
    finally:
        await application.state.rate_limit_redis.aclose()


app = FastAPI(
    title="Vistaro API",
    version="0.1.0",
    description="Vistaro AI Platform API",
    responses={
        500: {"model": ErrorEnvelope, "description": "Internal server error"},
    },
    lifespan=lifespan,
)

# Exception handlers
register_error_handlers(app)

# CORS is outermost so browser clients can read CSRF and rate-limit error envelopes.
app.include_router(auth_router)
app.add_middleware(CSRFMiddleware, web_origin=settings.web_origin)
app.add_middleware(
    RedisRateLimitMiddleware,
    limit=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware, app_env=settings.app_env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"],
)


# --- Response Schemas ---


class HealthResponse(BaseModel):
    """Liveness check response."""

    status: str = Field(default="ok", description="Process liveness status")
    environment: str = Field(description="Deployment environment name")


class DependencyChecks(BaseModel):
    """Breakdown of readiness dependency statuses."""

    database: str = Field(description="PostgreSQL connectivity status ('ok' or 'failed')")
    redis: str = Field(description="Redis connectivity status ('ok' or 'failed')")


class ReadyResponse(BaseModel):
    """Readiness check response."""

    status: str = Field(description="Readiness status ('ok' or 'unhealthy')")
    environment: str = Field(description="Deployment environment name")
    checks: DependencyChecks = Field(description="Individual dependency check results")


# --- Readiness Dependency Checkers ---


def check_database() -> bool:
    """Verify PostgreSQL connectivity with a short query."""
    try:
        engine = build_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_redis() -> bool:
    """Verify Redis broker/cache connectivity with a ping."""
    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
        return bool(client.ping())
    except Exception:
        return False


# Dependency checker hooks (allows deterministic testing of degraded states)
readiness_checkers: dict[str, Callable[[], bool]] = {
    "database": check_database,
    "redis": check_redis,
}


# --- System Endpoints ---


@app.get("/csrf", summary="Get a CSRF token", tags=["System"])
def csrf_token(request: Request, response: Response) -> dict[str, str]:
    """Issue a short-lived CSRF token, re-bound to a live session if present."""
    token = new_csrf_token()
    rebind_session_csrf(request, token)
    response.set_cookie(
        key="csrf_token",
        value=token,
        **csrf_cookie_options(settings.app_env),
    )
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": token}


@app.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Indicates whether the API process is alive.",
    responses={
        200: {"model": HealthResponse, "description": "Process is running"},
    },
    tags=["System"],
)
def healthz() -> HealthResponse:
    """Report whether the application process is alive."""
    return HealthResponse(status="ok", environment=settings.app_env)


@app.get(
    "/readyz",
    response_model=ReadyResponse,
    summary="Readiness check",
    description="Indicates whether the API and dependencies (Postgres, Redis) can serve traffic.",
    responses={
        200: {"model": ReadyResponse, "description": "All dependencies are healthy and ready"},
        503: {"model": ReadyResponse, "description": "One or more dependencies are unhealthy"},
    },
    tags=["System"],
)
def readyz(response: Response) -> ReadyResponse:
    """Report whether the service and required dependencies are ready to serve requests."""
    db_ok = readiness_checkers["database"]()
    redis_ok = readiness_checkers["redis"]()

    checks = DependencyChecks(
        database="ok" if db_ok else "failed",
        redis="ok" if redis_ok else "failed",
    )

    all_healthy = db_ok and redis_ok
    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadyResponse(
            status="unhealthy",
            environment=settings.app_env,
            checks=checks,
        )

    return ReadyResponse(
        status="ok",
        environment=settings.app_env,
        checks=checks,
    )

