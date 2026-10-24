"""HTTP middleware for request tracing and identification."""

import logging
import re
import uuid
from typing import Final

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER: Final[str] = "X-Request-ID"

# Validate incoming request IDs: 1 to 128 alphanumeric characters, dashes, or underscores.
# Never trust arbitrary incoming strings blindly.
REQUEST_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-zA-Z0-9_\-]{1,128}$")


def validate_request_id(raw_id: str | None) -> str | None:
    """Validate and sanitize an incoming request ID header.

    Returns the sanitized string if valid, or None if invalid/missing.
    """
    if not raw_id:
        return None
    cleaned = raw_id.strip()
    if REQUEST_ID_PATTERN.fullmatch(cleaned):
        return cleaned
    return None


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Ensure every HTTP request has a validated or newly generated request ID.

    Safe propagation guarantees:
    - Sets ``request.state.request_id``.
    - Adds the ``X-Request-ID`` header to the outgoing HTTP response.
    - Binds ``request_id`` to structlog contextvars for consistent logging.
    - Rejects malformed or oversized incoming request IDs in favor of a safe UUID.
    - Catches unhandled exceptions to ensure safe error responses and header presence.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming_id = request.headers.get(REQUEST_ID_HEADER)
        request_id = validate_request_id(incoming_id) or str(uuid.uuid4())

        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)
        except Exception as exc:
            from vistaro.core.errors import unhandled_exception_handler

            response = await unhandled_exception_handler(request, exc)
        finally:
            structlog.contextvars.unbind_contextvars("request_id")

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
