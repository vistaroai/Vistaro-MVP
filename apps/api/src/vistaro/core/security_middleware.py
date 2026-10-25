"""Security response headers, CSRF checks, and Redis-backed rate limiting."""

import logging
import time
from typing import Any

from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from vistaro.core.security import csrf_request_is_valid, security_headers

logger = logging.getLogger(__name__)

_RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply browser security headers to successful and error responses."""

    def __init__(self, app: Any, app_env: str) -> None:
        super().__init__(app)
        self.headers = security_headers(app_env)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for name, value in self.headers.items():
            response.headers.setdefault(name, value)
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """Reject unsafe browser requests without same-origin double-submit proof."""

    def __init__(self, app: Any, web_origin: str) -> None:
        super().__init__(app)
        self.web_origin = web_origin

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not csrf_request_is_valid(request, self.web_origin):
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "CSRF_VALIDATION_FAILED",
                        "message": "A valid same-origin CSRF token is required",
                        "details": None,
                    }
                },
            )
        return await call_next(request)


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    """Apply a fixed-window per-peer limit without trusting forwarded headers."""

    def __init__(
        self,
        app: Any,
        redis_client: Redis | None = None,
        limit: int = 120,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in {"/healthz", "/readyz"}:
            return await call_next(request)

        # The direct ASGI peer is used intentionally. Forwarded headers are untrusted
        # until a deployment explicitly configures trusted proxy handling.
        peer = request.client.host if request.client else "unknown"
        window = int(time.time()) // self.window_seconds
        key = f"vistaro:rate-limit:{peer}:{window}"
        try:
            redis_client = getattr(request.app.state, "rate_limit_redis", self.redis)
            if redis_client is None:
                raise RuntimeError("rate-limit Redis client is not initialized")
            count = int(await redis_client.eval(_RATE_LIMIT_SCRIPT, 1, key, self.window_seconds))
        except Exception as exc:
            logger.error("Redis rate-limit check failed", extra={"error_type": type(exc).__name__})
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "Request protection is temporarily unavailable",
                        "details": None,
                    }
                },
            )

        remaining = max(0, self.limit - count)
        response: Response
        if count > self.limit:
            retry_after = self.window_seconds - (int(time.time()) % self.window_seconds)
            response = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Too many requests",
                        "details": None,
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )
        else:
            response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
