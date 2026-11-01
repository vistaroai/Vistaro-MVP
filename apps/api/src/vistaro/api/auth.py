"""AUTH-001: email signup/login/verification (Phase A) + Google sign-in (Phase B).

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

from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import Connection, text

from vistaro.api.deps import SESSION_COOKIE_NAME, CurrentUser, _session_engine
from vistaro.core.config import settings
from vistaro.core.errors import (
    BadRequestError,
    ConflictError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from vistaro.core.security import (
    CSRF_COOKIE_NAME,
    csrf_cookie_options,
    new_csrf_token,
    session_cookie_options,
)
from vistaro.services.email import build_verification_email, get_email_sender
from vistaro.services.oauth_client import (
    GoogleUserInfo,
    google_client,
    parse_google_userinfo,
)
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


# --- Google sign-in (Phase B) ---

_GOOGLE_INSERT = text(
    "INSERT INTO users (id, email, password_hash, google_sub, email_verified_at)"
    " VALUES (:id, :email, NULL, :sub, now())"
)


def _link_or_create_google_user(info: GoogleUserInfo) -> uuid.UUID:
    """Find, link, or create the account behind a Google-verified identity.

    Trust model (documented decision): a Google token proves control of the
    Google account and that Google verified the email. We therefore:
    - reuse the account whose ``google_sub`` matches,
    - link an existing email-matching account that has no ``google_sub`` yet
      (the same proof-of-control as confirming an email address),
    - refuse accounts already bound to a DIFFERENT Google account (409) —
      the least surprising safe answer for a shared email conflict.
    Every write happens inside one transaction; the conflict raises before
    commit, so no partial link is ever stored.
    """
    lookup = text("SELECT id, google_sub FROM users WHERE email = :email")
    with _session_engine().begin() as connection:
        row = connection.execute(lookup, {"email": info.email}).mappings().first()
        if row is None:
            user_id = uuid.uuid4()
            connection.execute(
                _GOOGLE_INSERT,
                {"id": user_id, "email": info.email, "sub": info.sub},
            )
            return user_id
        existing_id = uuid.UUID(str(row["id"]))
        bound_sub = row["google_sub"]
        if bound_sub == info.sub:
            return existing_id
        if bound_sub is None:
            connection.execute(
                text("UPDATE users SET google_sub = :sub WHERE id = :id"),
                {"sub": info.sub, "id": existing_id},
            )
            return existing_id
        raise ConflictError(
            "This email is already linked to a different Google account",
            code="OAUTH_ACCOUNT_CONFLICT",
        )


def _insert_session_sync(user_id: uuid.UUID, csrf_token: str) -> str:
    """Insert one session row off the event loop; return the raw token."""
    with _session_engine().begin() as connection:
        return _insert_session(connection, user_id, csrf_token)


@router.get(
    "/google/login",
    name="google_login",
    summary="Start Google sign-in",
    responses={503: {"description": "Google credentials missing (feature off)"}},
)
async def google_login(request: Request) -> Response:
    """Redirect the browser to Google's consent screen (or answer 503).

    Authlib stores the anti-forgery ``state`` in the signed Starlette session
    (``SessionMiddleware`` with ``settings.session_secret``) and re-checks it
    during the token exchange, so this route needs no extra cookies.
    """
    client = google_client()
    if client is None:
        raise ServiceUnavailableError(
            "Google sign-in is not configured", code="OAUTH_NOT_CONFIGURED"
        )
    redirect_uri = request.url_for("google_callback")
    # Authlib is untyped; its Starlette client returns a RedirectResponse.
    redirect_response = await client.authorize_redirect(request, str(redirect_uri))
    return redirect_response  # type: ignore[no-any-return]


@router.get(
    "/google/callback",
    name="google_callback",
    summary="Finish Google sign-in",
    responses={400: {"description": "Generic sign-in failure envelope"}},
)
async def google_callback(request: Request, response: Response) -> AuthResponse:
    """Exchange the code, resolve the user, mint a session like login does.

    All failures (bad/outdated state, provider errors, missing/unverified
    email claims) share one generic envelope so nothing about the account
    leaks. The redirect to the web app lands with UI-001; for now the JSON
    body + cookies are the end of the flow.
    """
    client = google_client()
    if client is None:
        raise ServiceUnavailableError(
            "Google sign-in is not configured", code="OAUTH_NOT_CONFIGURED"
        )
    try:
        token_response = await client.authorize_access_token(request)
    except OAuthError:
        # Including the provider's own error text would leak flow internals.
        raise BadRequestError(
            "Google sign-in failed", code="OAUTH_FLOW_FAILED"
        ) from None
    info = parse_google_userinfo(token_response or {})
    if info is None:
        raise BadRequestError("Google sign-in failed", code="OAUTH_FLOW_FAILED")
    user_id = await run_in_threadpool(_link_or_create_google_user, info)
    csrf_token = new_csrf_token()
    session_token = await run_in_threadpool(_insert_session_sync, user_id, csrf_token)
    _set_auth_cookies(response, session_token, csrf_token)
    return AuthResponse(
        user=UserOut(id=str(user_id), email=info.email, email_verified=True),
        csrf_token=csrf_token,
    )


# --- Endpoints (email flows, Phase A) ---


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

