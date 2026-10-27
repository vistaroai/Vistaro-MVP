"""Request-level dependencies shared by feature routers (AUTH-001).

``get_current_user`` resolves the session cookie to the account and enforces
the session-bound CSRF check (WARN-E-006, the SEC-001 follow-through for
auth): on unsafe methods the double-submit token must exist, match its
cookie, and hash to the hash stored on the session row.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, Request
from sqlalchemy import Engine, text

from vistaro.core.config import settings
from vistaro.core.errors import ForbiddenError, UnauthorizedError
from vistaro.core.security import CSRF_COOKIE_NAME, CSRF_HEADER_NAME, SAFE_METHODS
from vistaro.db.tenancy import build_engine
from vistaro.services.tokens import token_digest

SESSION_COOKIE_NAME = "vistaro_session"


@lru_cache
def _session_engine() -> Engine:
    """Process-wide engine for session lookups (vistaro_app role)."""
    return build_engine(settings.database_url)


@dataclass(frozen=True)
class AuthenticatedUser:
    """The account bound to the current request's session."""

    user_id: str
    email: str
    email_verified_at: datetime | None
    session_id_hash: str


def _load_session(request: Request) -> tuple[dict[str, Any], str] | None:
    """Fetch the session row joined with the user, or ``None``.

    Returns the row mapping plus the digest that was looked up, so callers
    can refresh ``last_seen_at`` without re-deriving it.
    """
    raw_token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not raw_token:
        return None
    id_hash = token_digest(raw_token)
    query = text(
        "SELECT s.user_id, s.csrf_token_hash, s.expires_at,"
        " u.email, u.email_verified_at"
        " FROM sessions s JOIN users u ON u.id = s.user_id"
        " WHERE s.id_hash = :id_hash"
    )
    with _session_engine().connect() as connection:
        row = connection.execute(query, {"id_hash": id_hash}).mappings().first()
    if row is None:
        return None
    expires_at = row["expires_at"]
    if not isinstance(expires_at, datetime):
        return None
    if datetime.now(tz=UTC) >= expires_at:
        return None
    return dict(row), id_hash


def get_current_user(request: Request) -> AuthenticatedUser:
    """Resolve the authenticated user or fail with a generic 401/403.

    The same error is returned for missing, forged, and expired sessions, so
    nothing distinguishes the cases outside the log. A presented cookie can
    never hijack another account: login mints a brand new session id and the
    presented value is only ever resolved by digest (session-fixation test).
    """
    loaded = _load_session(request)
    if loaded is None:
        raise UnauthorizedError(
            "Sign in to continue",
            code="SESSION_INVALID",
        )
    row, id_hash = loaded

    if request.method.upper() not in SAFE_METHODS:
        # Session-bound check on top of the CSRF middleware, which already
        # required same-origin and cookie == header (SEC-001 baseline).
        client_token = request.cookies.get(CSRF_COOKIE_NAME, "")
        header_token = request.headers.get(CSRF_HEADER_NAME, "")
        bound_hash = row["csrf_token_hash"]
        token_ok = (
            isinstance(bound_hash, str)
            and bool(client_token)
            and bool(header_token)
            and token_digest(client_token) == bound_hash
            and token_digest(header_token) == bound_hash
        )
        if not token_ok:
            raise ForbiddenError(
                "A session-bound CSRF token is required",
                code="CSRF_VALIDATION_FAILED",
            )

    refresh = text("UPDATE sessions SET last_seen_at = now() WHERE id_hash = :id_hash")
    with _session_engine().begin() as connection:
        connection.execute(refresh, {"id_hash": id_hash})

    return AuthenticatedUser(
        user_id=str(row["user_id"]),
        email=str(row["email"]),
        email_verified_at=row["email_verified_at"],
        session_id_hash=id_hash,
    )


def rebind_session_csrf(request: Request, token: str) -> None:
    """Re-tie an existing session's stored CSRF hash to a fresh token.

    Called by ``GET /csrf`` when the caller carries a live session: clients
    may safely refetch a CSRF pair at any time and the new single-use pair
    stays bound to that one session (WARN-E-006). No-op without a session.
    """
    raw_token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not raw_token:
        return
    id_hash = token_digest(raw_token)
    update = text(
        "UPDATE sessions SET csrf_token_hash = :new_hash"
        " WHERE id_hash = :id_hash"
    )
    with _session_engine().begin() as connection:
        connection.execute(
            update,
            {"new_hash": token_digest(token), "id_hash": id_hash},
        )


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
