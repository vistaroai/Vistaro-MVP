"""FastAPI application entry point."""

from collections.abc import Callable

import redis
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text

from vistaro.core.config import settings
from vistaro.core.errors import ErrorEnvelope, register_error_handlers
from vistaro.core.middleware import RequestIDMiddleware
from vistaro.db.tenancy import build_engine

app = FastAPI(
    title="Vistaro API",
    version="0.1.0",
    description="Vistaro AI Platform API",
    responses={
        500: {"model": ErrorEnvelope, "description": "Internal server error"},
    },
)

# Exception handlers
register_error_handlers(app)

# Middlewares (RequestIDMiddleware outermost to trace all requests and errors)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(RequestIDMiddleware)


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
