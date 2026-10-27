"""AUTH-001 (Phase A): email signup, login, logout, verification, sessions.

Google sign-in lands in Phase B once the founders create OAuth credentials.

Design contract:
- Passwords: Argon2id via ``services.passwords`` (no hand-rolled crypto).
- Sessions: server-side rows; the browser cookie holds a random token whose
  SHA-256 is the ``sessions.id_hash``; expiry is absolute
  (``settings.session_lifetime_seconds``). Every login mints a brand new
  session id (session fixation defense) and binds the CSRF token to the
  session (``sessions.csrf_token_hash``, WARN-E-006).
- Emails: verification tokens are single-use, digest-stored, expiring; links
  point at ``GET /auth/verify`` until the web page exists (UI-001).
- Errors: login never distinguishes unknown email from wrong password
  (``INVALID_CREDENTIALS``), and all verification-link failures share one
  envelope, so account existence never leaks.
- Never logs request bodies, email bodies, or tokens (they are secrets).
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import Connection, text

from vistaro.api.deps import SESSION_COOKIE_NAME, CurrentUser, _session_engine
from vistaro.core.config import settings
from vistaro.core.errors import BadRequestError, ConflictError, UnauthorizedError
from vistaro.core.security import (
    CSRF_COOKIE_NAME,
    csrf_cookie_options,
    new_csrf_token,
    session_cookie_options,
)
from vistaro.services.email import build_verification_email, get_email_sender
from vistaro.services.passwords import hash_password, verify_login_attempt
from vistaro.services.tokens import generate_token, token_digest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


class SignupRequest(BaseModel):
    """Signup payload: an email and a password of at least 10 characters."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=10, max_length=1024)

    @field_validator("password")
    @classmethod
    def reject_control_characters(cls, value: str) -> str:
        """Reject passwords whose NUL/CR/LF could be mangled or split."""
        if "\x00" in value or "\r" in value or "\n" in value:
            raise ValueError("Password must not contain control characters")
        return value


class UserOut(BaseModel):
    """Public account fields. Never includes ``password_hash``."""

    model_config = ConfigDict(extra="forbid")

    id: str
    email: str
    email_verified: bool


class AuthResponse(BaseModel):
    """Body of signup/login: the user plus the session-bound CSRF token."""

    model_config = ConfigDict(extra="forbid")

    user: UserOut
    csrf_token: str


class VerifyResponse(BaseModel):
    """Body of a successful verification link visit."""

    model_config = ConfigDict(extra="forbid")

    email_verified: bool


def _link_invalid() -> BadRequestError:
    """Build the one shared envelope for every failed verification link."""
    return BadRequestError(
        "This verification link is invalid, expired, or already used",
        code="VERIFICATION_LINK_INVALID",
    )


# --- Internal helpers ---


def _set_auth_cookies(response: Response, session_token: str, csrf_token: str) -> None:
    """Set the HttpOnly session cookie and the readable CSRF cookie."""
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        max_age=settings.session_lifetime_seconds,
        **session_cookie_options(settings.app_env),
    )
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        **csrf_cookie_options(settings.app_env),
    )


def _insert_session(
    connection: Connection, user_id: uuid.UUID, csrf_token: str
) -> str:
    """Insert one session row and return the raw session token.

    Always mints a brand new session id (fixation defense) and hashes the
    CSRF token onto the session row (session-bound CSRF). Caller passes an
    open transaction; cookie-setting happens after commit.
    """
    session_token = generate_token()
    expires_at = datetime.now(tz=UTC) + timedelta(seconds=settings.session_lifetime_seconds)
    connection.execute(
        text(
            "INSERT INTO sessions (id_hash, user_id, active_workspace_id,"
            " created_at, last_seen_at, expires_at, csrf_token_hash)"
            " VALUES (:id_hash, :user_id, NULL, now(), now(), :expires_at, :csrf_hash)"
        ),
        {
            "id_hash": token_digest(session_token),
            "user_id": user_id,
            "expires_at": expires_at,
            "csrf_hash": token_digest(csrf_token),
        },
    )
    return session_token


def _lookup_user(email: str) -> dict[str, object] | None:
    """Load ``id, password_hash, email_verified_at`` for one email."""
    query = text(
        "SELECT id, password_hash, email_verified_at FROM users WHERE email = :email"
    )
    with _session_engine().connect() as connection:
        row = connection.execute(query, {"email": email}).mappings().first()
    return dict(row) if row is not None else None


def _send_verification(user_id: uuid.UUID, email: str) -> None:
    """Create one signup token row and deliver its link. Never raises.

    A delivery failure must not fail the signup; the link is re-issued by a
    fresh signup once the address is free again (not merging that path yet).
    """
    token = generate_token()
    subject, body = build_verification_email(token, email)
    try:
        with _session_engine().begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO email_verifications"
                    " (id, user_id, token_hash, purpose, expires_at)"
                    " VALUES (:id, :user_id, :token_hash, 'signup', :expires_at)"
                ),
                {
                    "id": uuid.uuid4(),
                    "user_id": user_id,
                    "token_hash": token_digest(token),
                    "expires_at": datetime.now(tz=UTC)
                    + timedelta(seconds=settings.verification_token_ttl_seconds),
                },
            )
        get_email_sender().send(email, subject, body)
    except Exception:  # noqa: BLE001 - email failure must not fail signup
        logger.exception("verification email delivery failed for user %s", user_id)


# --- Endpoints ---


@router.post(
    "/signup",
    status_code=201,
    summary="Create an account and start a session",
    responses={409: {"description": "Email already registered"}},
)
def signup(request_data: SignupRequest, response: Response) -> AuthResponse:
    """Create the ``users`` row unverified, issue a session, email the link.

    By design signup reveals registration truthfully: the duplicate case
    answers 409 explicitly (the anti-enumeration rule is applied on login).
    """
    if _lookup_user(request_data.email) is not None:
        raise ConflictError(
            "An account with this email already exists",
            code="EMAIL_ALREADY_IN_USE",
        )

    user_id = uuid.uuid4()
    csrf_token = new_csrf_token()
    session_token: str
    with _session_engine().begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (id, email, password_hash)"
                " VALUES (:id, :email, :password_hash)"
            ),
            {
                "id": user_id,
                "email": request_data.email,
                "password_hash": hash_password(request_data.password),
            },
        )
        session_token = _insert_session(connection, user_id, csrf_token)

    _set_auth_cookies(response, session_token, csrf_token)
    _send_verification(user_id, request_data.email)
    return AuthResponse(
        user=UserOut(
            id=str(user_id), email=request_data.email, email_verified=False
        ),
        csrf_token=csrf_token,
    )


@router.post(
    "/login",
    summary="Sign in with an email and password",
    responses={401: {"description": "Wrong email or password (same envelope for both)"}},
)
def login(request_data: SignupRequest, response: Response) -> AuthResponse:
    """Verify Argon2id credentials and mint a fresh session with bound CSRF.

    Unknown accounts burn the same Argon2id work as a wrong password so
    timing cannot enumerate emails.
    """
    row = _lookup_user(request_data.email)
    is_valid = verify_login_attempt(
        row["password_hash"] if row else None,  # type: ignore[arg-type]
        request_data.password,
    )
    if row is None or not is_valid:
        # Same status, code, and message for both failure causes.
        raise UnauthorizedError(
            "Email or password is incorrect", code="INVALID_CREDENTIALS"
        )

    user_id = uuid.UUID(str(row["id"]))
    csrf_token = new_csrf_token()
    session_token: str
    with _session_engine().begin() as connection:
        session_token = _insert_session(connection, user_id, csrf_token)

    _set_auth_cookies(response, session_token, csrf_token)
    return AuthResponse(
        user=UserOut(
            id=str(user_id),
            email=request_data.email,
            email_verified=row["email_verified_at"] is not None,
        ),
        csrf_token=csrf_token,
    )


@router.post(
    "/logout",
    summary="Delete the current session",
    responses={401: {"description": "No valid session"}},
)
def logout(user: CurrentUser, response: Response) -> dict[str, str]:
    """Remove the session row and clear both cookies.

    Requires the session-bound CSRF token (enforced by ``CurrentUser`` on
    this unsafe method).
    """
    with _session_engine().begin() as connection:
        connection.execute(
            text("DELETE FROM sessions WHERE id_hash = :id_hash"),
            {"id_hash": user.session_id_hash},
        )
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(CSRF_COOKIE_NAME, path="/")
    return {"status": "ok"}


@router.get("/me", summary="Current account summary")
def me(user: CurrentUser) -> UserOut:
    """Return the caller's own account summary (no secrets)."""
    return UserOut(
        id=user.user_id,
        email=user.email,
        email_verified=user.email_verified_at is not None,
    )


@router.get(
    "/verify",
    summary="Confirm an email address with a one-time link",
    responses={400: {"description": "Invalid, expired, or already-used link"}},
)
def verify(token: str | None = None) -> VerifyResponse:
    """Consume one verification token and mark the account verified.

    All failure modes (garbage token, expired, reused) return one identical
    envelope, so nothing about account state leaks through timing or text.
    Email-link rotation of any live session arrives with the browser flows
    (Phase B); server-side verification is idempotent-safe via ``consumed_at``.
    """
    if not token:
        raise _link_invalid()
    token_hash = token_digest(token)
    lookup = text(
        "SELECT ev.id, ev.user_id, ev.expires_at, ev.consumed_at"
        " FROM email_verifications ev WHERE ev.token_hash = :token_hash"
    )
    with _session_engine().connect() as connection:
        row = connection.execute(lookup, {"token_hash": token_hash}).mappings().first()

    if row is None or row["consumed_at"] is not None:
        raise _link_invalid()
    if datetime.now(tz=UTC) >= row["expires_at"]:
        raise _link_invalid()

    with _session_engine().begin() as connection:
        connection.execute(
            text(
                "UPDATE users SET email_verified_at = now() WHERE id = :user_id"
            ),
            {"user_id": row["user_id"]},
        )
        connection.execute(
            text("UPDATE email_verifications SET consumed_at = now() WHERE id = :id"),
            {"id": row["id"]},
        )
    return VerifyResponse(email_verified=True)

