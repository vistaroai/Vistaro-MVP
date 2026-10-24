"""Typed API exceptions, error envelope schemas, and exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Inner error payload containing code, message, and optional details."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")
    details: Any = Field(default=None, description="Optional structured error details")


class ErrorEnvelope(BaseModel):
    """Standard Vistaro API error envelope."""

    model_config = ConfigDict(extra="forbid")

    error: ErrorDetail


class APIError(Exception):
    """Base class for all typed API exceptions.

    Serializes to ``{"error": {"code": ..., "message": ..., "details": ...}}``.
    """

    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        details: Any = None,
        status_code: int | None = None,
    ) -> None:
        self.message = message if message is not None else self.message
        self.code = code if code is not None else self.code
        self.details = details
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)

    def to_envelope(self) -> dict[str, Any]:
        """Convert the exception to the standard error dictionary."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class BadRequestError(APIError):
    """HTTP 400 Bad Request."""

    status_code = 400
    code = "BAD_REQUEST"
    message = "Bad request"


class UnauthorizedError(APIError):
    """HTTP 401 Unauthorized."""

    status_code = 401
    code = "UNAUTHORIZED"
    message = "Authentication required"


class ForbiddenError(APIError):
    """HTTP 403 Forbidden."""

    status_code = 403
    code = "PERMISSION_DENIED"
    message = "Permission denied"


# Aliases per repository conventions
PermissionDenied = ForbiddenError
PermissionDeniedError = ForbiddenError


class NotFoundError(APIError):
    """HTTP 404 Not Found."""

    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"


NotFound = NotFoundError


class MethodNotAllowedError(APIError):
    """HTTP 405 Method Not Allowed."""

    status_code = 405
    code = "METHOD_NOT_ALLOWED"
    message = "Method not allowed"


class ConflictError(APIError):
    """HTTP 409 Conflict."""

    status_code = 409
    code = "CONFLICT"
    message = "Resource conflict"


Conflict = ConflictError


class ValidationFailedError(APIError):
    """HTTP 422 Unprocessable Entity / Validation Failed."""

    status_code = 422
    code = "VALIDATION_FAILED"
    message = "Validation failed"


ValidationFailed = ValidationFailedError


class RateLimitedError(APIError):
    """HTTP 429 Too Many Requests."""

    status_code = 429
    code = "RATE_LIMITED"
    message = "Too many requests"


class ServiceUnavailableError(APIError):
    """HTTP 503 Service Unavailable."""

    status_code = 503
    code = "SERVICE_UNAVAILABLE"
    message = "Service unavailable"


def _status_code_to_error_code(status_code: int) -> str:
    """Map common HTTP status codes to standard error code strings."""
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "PERMISSION_DENIED",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_FAILED",
        429: "RATE_LIMITED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }
    return mapping.get(status_code, f"HTTP_{status_code}")


async def api_error_handler(_request: Request, exc: APIError) -> JSONResponse:
    """Handle application-defined APIError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_envelope(),
    )


async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI / Pydantic request validation errors in standard envelope."""
    # Format details safely without non-serializable objects
    details: list[dict[str, Any]] = []
    for err in exc.errors():
        details.append(
            {
                "loc": list(err.get("loc", [])),
                "msg": err.get("msg", ""),
                "type": err.get("type", ""),
            }
        )
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_FAILED",
                "message": "Request validation failed",
                "details": details,
            }
        },
    )


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette / FastAPI HTTPException in standard envelope."""
    code = _status_code_to_error_code(exc.status_code)
    message = str(exc.detail) if exc.detail else "HTTP error"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": None,
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any uncaught exception without leaking internals or credentials."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled server exception [request_id=%s]: %s", request_id, exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": None,
            }
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register all standard error handlers on the FastAPI app."""
    app.add_exception_handler(APIError, api_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
