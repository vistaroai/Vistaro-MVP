"""Small, reusable browser security controls for the API."""

import secrets
from typing import Literal, TypedDict
from urllib.parse import urlsplit

from starlette.requests import Request

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"


class SessionCookieOptions(TypedDict):
    httponly: bool
    secure: bool
    samesite: Literal["lax", "none"]
    path: str


class CSRFCookieOptions(TypedDict):
    httponly: Literal[False]
    secure: bool
    samesite: Literal["lax", "none"]
    path: str
    max_age: int


def session_cookie_options(app_env: str) -> SessionCookieOptions:
    """Return secure defaults for a future session cookie; does not issue one."""
    local = app_env == "local"
    return {
        "httponly": True,
        "secure": not local,
        "samesite": "lax" if local else "none",
        "path": "/",
    }


def csrf_cookie_options(app_env: str) -> CSRFCookieOptions:
    """Return attributes for the readable double-submit CSRF cookie."""
    local = app_env == "local"
    return {
        "httponly": False,
        "secure": not local,
        "samesite": "lax" if local else "none",
        "path": "/",
        "max_age": 3600,
    }


def security_headers(app_env: str) -> dict[str, str]:
    """Headers appropriate for a JSON API with FastAPI's interactive docs."""
    headers = {
        "Content-Security-Policy": (
            "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; connect-src 'self'"
        ),
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
    }
    if app_env in {"staging", "production"}:
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return headers


def _origin_tuple(origin: str | None) -> tuple[str, str, int | None] | None:
    if not origin:
        return None
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    if parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    scheme = parsed.scheme.lower()
    return scheme, parsed.hostname.lower(), port or (443 if scheme == "https" else 80)


def csrf_request_is_valid(request: Request, web_origin: str) -> bool:
    """Require same-origin browser intent and a matching double-submit token."""
    if request.method.upper() in SAFE_METHODS:
        return True
    expected_origin = _origin_tuple(web_origin)
    received_origin = _origin_tuple(request.headers.get("origin"))
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME, "")
    header_token = request.headers.get(CSRF_HEADER_NAME, "")
    return bool(
        expected_origin
        and received_origin == expected_origin
        and cookie_token
        and header_token
        and secrets.compare_digest(cookie_token, header_token)
    )


def new_csrf_token() -> str:
    """Generate an unpredictable token for the double-submit cookie pattern."""
    return secrets.token_urlsafe(32)
