"""Contract tests for standard API error envelope and typed exceptions."""

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from vistaro.core.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitedError,
    ServiceUnavailableError,
    ValidationFailedError,
    register_error_handlers,
)
from vistaro.core.middleware import REQUEST_ID_HEADER, RequestIDMiddleware


class DummyBody(BaseModel):
    name: str
    count: int


def create_test_app() -> FastAPI:
    test_app = FastAPI()
    register_error_handlers(test_app)
    test_app.add_middleware(RequestIDMiddleware)

    router = APIRouter()

    @router.get("/error/bad-request")
    def trigger_bad_request() -> None:
        raise BadRequestError("Bad request test", details={"field": "test"})

    @router.get("/error/not-found")
    def trigger_not_found() -> None:
        raise NotFoundError("Resource missing")

    @router.get("/error/forbidden")
    def trigger_forbidden() -> None:
        raise ForbiddenError("Access denied")

    @router.get("/error/conflict")
    def trigger_conflict() -> None:
        raise ConflictError("Resource already exists")

    @router.get("/error/validation")
    def trigger_validation() -> None:
        raise ValidationFailedError("Validation failure")

    @router.get("/error/rate-limited")
    def trigger_rate_limited() -> None:
        raise RateLimitedError("Too many calls")

    @router.get("/error/service-unavailable")
    def trigger_service_unavailable() -> None:
        raise ServiceUnavailableError("Upstream unavailable")

    @router.post("/error/schema-validation")
    def trigger_schema_validation(body: DummyBody) -> dict[str, str]:
        return {"name": body.name}

    @router.get("/error/unhandled")
    def trigger_unhandled() -> None:
        raise RuntimeError("Secret internal failure message with credentials db://user:secret@host")

    test_app.include_router(router)
    return test_app


client = TestClient(create_test_app(), raise_server_exceptions=False)


def test_bad_request_envelope() -> None:
    response = client.get("/error/bad-request")
    assert response.status_code == 400
    assert REQUEST_ID_HEADER in response.headers
    data = response.json()
    assert data == {
        "error": {
            "code": "BAD_REQUEST",
            "message": "Bad request test",
            "details": {"field": "test"},
        }
    }


def test_not_found_envelope() -> None:
    response = client.get("/error/not-found")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource missing",
            "details": None,
        }
    }


def test_forbidden_envelope() -> None:
    response = client.get("/error/forbidden")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"


def test_conflict_envelope() -> None:
    response = client.get("/error/conflict")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_validation_failed_envelope() -> None:
    response = client.get("/error/validation")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_FAILED"


def test_rate_limited_envelope() -> None:
    response = client.get("/error/rate-limited")
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "RATE_LIMITED"


def test_service_unavailable_envelope() -> None:
    response = client.get("/error/service-unavailable")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_fastapi_request_validation_envelope() -> None:
    # Send malformed payload to trigger FastAPI/Pydantic RequestValidationError
    response = client.post("/error/schema-validation", json={"name": 123, "count": "not-an-int"})
    assert response.status_code == 422
    assert REQUEST_ID_HEADER in response.headers
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_FAILED"
    assert data["error"]["message"] == "Request validation failed"
    assert isinstance(data["error"]["details"], list)
    assert len(data["error"]["details"]) > 0


def test_starlette_not_found_route_envelope() -> None:
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    assert REQUEST_ID_HEADER in response.headers
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"


def test_unhandled_exception_does_not_leak_internals() -> None:
    response = client.get("/error/unhandled")
    assert response.status_code == 500
    assert REQUEST_ID_HEADER in response.headers
    data = response.json()
    assert data == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": None,
        }
    }
    # Crucial security check: internal error string and secret credentials never leak
    raw_text = response.text
    assert "Secret internal failure" not in raw_text
    assert "secret" not in raw_text
