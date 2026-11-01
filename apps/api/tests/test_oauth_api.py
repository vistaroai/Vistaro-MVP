"""AUTH-001 Phase B API tests: Google sign-in against a FAKE provider.

The network-facing Authlib behavior (metadata discovery, token exchange,
state validation) cannot run in CI, so the ``google_client`` symbol is
swapped for a ``FakeGoogleClient`` that mirrors its interface. What these
tests DO enforce: feature toggle (503), account find/link/create rules,
session minting on success, and one generic failure envelope for every
Google-side problem so account state never leaks.
"""

from collections.abc import Iterator
from typing import Any

import pytest
from authlib.integrations.base_client.errors import OAuthError
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from vistaro.api.deps import SESSION_COOKIE_NAME
from vistaro.core.config import settings
from vistaro.core.security import CSRF_COOKIE_NAME
from vistaro.main import app as api_app
from vistaro.services.oauth_client import parse_google_userinfo

EMAIL = "google-user@example.com"
SUB = "google-sub-1"
ORIGIN = "http://localhost:5173"


class FakeGoogleClient:
    """Stands in for Authlib's Starlette client (same method surface)."""

    def __init__(
        self,
        token_response: dict[str, Any] | None = None,
        provider_error: bool = False,
    ) -> None:
        self.captured_redirect_uri: str | None = None
        self.token_response = token_response
        self.provider_error = provider_error

    async def authorize_redirect(self, request: Any, redirect_uri: str) -> RedirectResponse:
        self.captured_redirect_uri = redirect_uri
        return RedirectResponse(
            "https://accounts.google.com/o/oauth2/auth?client_id=fake&state=fake-state",
            status_code=302,
        )

    async def authorize_access_token(self, request: Any) -> dict[str, Any]:
        if self.provider_error:
            raise OAuthError("invalid_state")
        return self.token_response or {}


def userinfo(sub: str = SUB, email: str = EMAIL, verified: bool = True) -> dict[str, Any]:
    """One canonical fake userinfo claim (configurable per test)."""
    return {"sub": sub, "email": email, "email_verified": verified}


@pytest.fixture(name="oauth")
def fixture_oauth(
    monkeypatch: pytest.MonkeyPatch, app_engine: Engine, admin_engine: Engine
) -> Iterator[tuple[TestClient, FakeGoogleClient]]:
    """Fresh users table plus a FakeGoogleClient wired into the routes."""
    with admin_engine.begin() as connection:
        connection.execute(text("TRUNCATE sessions, email_verifications, users CASCADE"))
    fake = FakeGoogleClient()
    monkeypatch.setattr("vistaro.api.auth.google_client", lambda: fake)
    try:
        with TestClient(api_app, base_url="http://testserver") as client:
            yield client, fake
    finally:
        with admin_engine.begin() as connection:
            connection.execute(
                text("TRUNCATE sessions, email_verifications, users CASCADE")
            )


def user_row(engine: Engine, email: str) -> dict[str, object] | None:
    """Load one user row straight through the app-role engine."""
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT id, google_sub, password_hash, email_verified_at"
                " FROM users WHERE email = :email"
            ),
            {"email": email},
        ).mappings().first()
    return dict(row) if row is not None else None


def user_count(engine: Engine, email: str) -> int:
    """Count rows for one email (duplicate-prevention assertions)."""
    with engine.connect() as connection:
        return int(
            connection.execute(
                text("SELECT count(*) FROM users WHERE email = :email"),
                {"email": email},
            ).scalar_one()
        )


def callback(client: TestClient, code: str = "a", state: str = "s") -> Any:
    """One callback GET without following redirects."""
    return client.get(
        f"/auth/google/callback?code={code}&state={state}", follow_redirects=False
    )


# --- Feature toggle ---


def test_google_login_off_when_unconfigured(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no credentials the route answers 503 and touches no network."""
    monkeypatch.setattr(settings, "google_client_id", "")
    monkeypatch.setattr(settings, "google_client_secret", "")
    with TestClient(api_app, base_url="http://testserver") as client:
        response = client.get("/auth/google/login")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "OAUTH_NOT_CONFIGURED"


def test_google_login_redirects_to_consent(
    oauth: tuple[TestClient, FakeGoogleClient]
) -> None:
    client, fake = oauth
    response = client.get("/auth/google/login", follow_redirects=False)
    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["location"]
    assert fake.captured_redirect_uri == "http://testserver/auth/google/callback"


# --- Success paths ---


def test_google_callback_creates_verified_passwordless_user(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    fake.token_response = {"userinfo": userinfo()}
    response = callback(client)
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == EMAIL
    assert body["user"]["email_verified"] is True
    assert client.cookies.get(SESSION_COOKIE_NAME)
    assert client.cookies.get(CSRF_COOKIE_NAME)

    row = user_row(app_engine, EMAIL)
    assert row is not None
    assert str(row["google_sub"]) == SUB
    assert row["password_hash"] is None  # no password exists for this account
    assert row["email_verified_at"] is not None

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == EMAIL


def test_google_callback_reuses_same_google_account(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    fake.token_response = {"userinfo": userinfo()}
    assert callback(client).status_code == 200
    assert callback(client).status_code == 200
    assert user_count(app_engine, EMAIL) == 1  # found, not re-created
    assert str(user_row(app_engine, EMAIL)["google_sub"]) == SUB


def test_google_callback_links_existing_password_account(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    # Register with a password first (Phase A flow), then sign in with Google.
    csrf = client.get("/csrf").json()["csrf_token"]
    signup = client.post(
        "/auth/signup",
        json={"email": EMAIL, "password": "correct-horse-battery-staple"},
        headers={"Origin": ORIGIN, "X-CSRF-Token": csrf},
    )
    assert signup.status_code == 201
    assert user_row(app_engine, EMAIL)["google_sub"] is None

    fake.token_response = {"userinfo": userinfo()}
    response = callback(client)
    assert response.status_code == 200
    row = user_row(app_engine, EMAIL)
    assert str(row["google_sub"]) == SUB
    assert row["password_hash"] is not None  # link keeps the password intact
    assert user_count(app_engine, EMAIL) == 1  # linked, not duplicated


# --- Failure paths ---


def test_google_callback_conflict_when_email_bound_to_other_google_account(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    fake.token_response = {"userinfo": userinfo()}
    assert callback(client).status_code == 200

    fake.token_response = {"userinfo": userinfo(sub="google-sub-DIFFERENT")}
    conflict = callback(client, code="b")
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "OAUTH_ACCOUNT_CONFLICT"
    # The original binding must be untouched.
    assert str(user_row(app_engine, EMAIL)["google_sub"]) == SUB


def test_google_provider_error_is_generic(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    fake.provider_error = True
    response = callback(client, state="bad")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "OAUTH_FLOW_FAILED"
    assert user_row(app_engine, EMAIL) is None  # nothing was created


def test_google_unverified_email_is_generic(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    fake.token_response = {"userinfo": userinfo(verified=False)}
    response = callback(client)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "OAUTH_FLOW_FAILED"
    assert user_row(app_engine, EMAIL) is None


def test_google_missing_userinfo_is_generic(
    oauth: tuple[TestClient, FakeGoogleClient],
    app_engine: Engine,
) -> None:
    client, fake = oauth
    fake.token_response = {"access_token": "x"}  # no userinfo claim
    response = callback(client)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "OAUTH_FLOW_FAILED"
    assert user_row(app_engine, EMAIL) is None


# --- Pure-parse unit checks (no DB) ---


def test_parse_google_userinfo_accepts_verified_claims() -> None:
    info = parse_google_userinfo({"userinfo": userinfo()})
    assert info is not None
    assert info.sub == SUB
    assert info.email == EMAIL


def test_parse_google_userinfo_rejects_every_failure_shape() -> None:
    bad_responses: list[Any] = [
        {},
        None,
        {"userinfo": None},
        {"userinfo": {"email": EMAIL, "email_verified": True}},  # no sub
        {"userinfo": {"sub": SUB, "email_verified": True}},  # no email
        {"userinfo": userinfo(verified=False)},  # unverified
        {"userinfo": userinfo(sub="")},
        {"userinfo": userinfo(email=None)},
    ]
    for bad in bad_responses:
        assert parse_google_userinfo(bad) is None, bad
