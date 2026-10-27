"""AUTH-001 (Phase A) API tests: signup, login, logout, verify, sessions.

These exercise the real app against the real Postgres (app-role engine) plus
a FAKE email sender; the Mailpit delivery itself is exercised in
``test_auth_units.py``. Every failure envelope is asserted so a regression
that leaks account existence shows up as a test failure.
"""

import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from vistaro.api.deps import SESSION_COOKIE_NAME
from vistaro.core.security import CSRF_COOKIE_NAME
from vistaro.main import app as api_app
from vistaro.services.email import VERIFY_PATH, RecordingEmailSender
from vistaro.services.tokens import generate_token

ORIGIN = "http://localhost:5173"
PASSWORD = "correct-horse-battery-staple"


@dataclass
class Harness:
    """TestClient with the FAKE sender already plugged in."""

    client: TestClient
    sender: RecordingEmailSender


@pytest.fixture(name="auth")
def fixture_auth(
    monkeypatch: pytest.MonkeyPatch, app_engine: Engine, admin_engine: Engine
) -> Iterator[Harness]:
    """Truncate user tables, run with the FAKE email sender, truncate again."""
    with admin_engine.begin() as connection:
        connection.execute(text("TRUNCATE sessions, email_verifications, users CASCADE"))
    sender = RecordingEmailSender()
    monkeypatch.setattr("vistaro.api.auth.get_email_sender", lambda: sender)
    with TestClient(api_app, base_url="http://testserver") as client:
        try:
            yield Harness(client=client, sender=sender)
        finally:
            with admin_engine.begin() as connection:
                connection.execute(
                    text("TRUNCATE sessions, email_verifications, users CASCADE")
                )


def sync_csrf(client: TestClient) -> dict[str, str]:
    """Fetch a CSRF cookie and return the headers required for POSTs."""
    token = client.get("/csrf").json()["csrf_token"]
    return {"Origin": ORIGIN, "X-CSRF-Token": token}


def signup(
    harness: Harness,
    email: str = "user@example.com",
    password: str = PASSWORD,
) -> TestClient:
    """One signup request with a valid CSRF pair."""
    return harness.client.post(
        "/auth/signup",
        json={"email": email, "password": password},
        headers=sync_csrf(harness.client),
    )


def verification_token(harness: Harness) -> str:
    """Extract the one-time token from the FAKE sender's recorded link."""
    assert harness.sender.sent, "expected a recorded verification email"
    link = harness.sender.sent[0].body.splitlines()[4]
    query = parse_qs(urlsplit(link).query)
    return str(query["token"][0])


# --- Signup ---


def test_signup_creates_user_session_and_email(auth: Harness) -> None:
    response = signup(auth)
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "user@example.com"
    assert body["user"]["email_verified"] is False
    assert "password_hash" not in body["user"]
    assert body["csrf_token"]
    # Both cookies are present: HttpOnly session and readable CSRF.
    assert auth.client.cookies.get(SESSION_COOKIE_NAME)
    assert auth.client.cookies.get(CSRF_COOKIE_NAME)
    assert len(auth.sender.sent) == 1
    assert auth.sender.sent[0].to_email == "user@example.com"
    assert VERIFY_PATH in auth.sender.sent[0].body


def test_signup_rejects_duplicate_email(auth: Harness) -> None:
    signup(auth)
    second = signup(auth)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "EMAIL_ALREADY_IN_USE"


def test_signup_rejects_short_password(auth: Harness) -> None:
    response = signup(auth, password="short")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_FAILED"


def test_verification_email_never_carries_the_password(auth: Harness) -> None:
    signup(auth)
    recorded = auth.sender.sent[0].body + auth.sender.sent[0].subject
    assert PASSWORD not in recorded


# --- Login ---


def test_login_success_mints_fresh_session(auth: Harness) -> None:
    signup(auth)
    first_session = auth.client.cookies.get(SESSION_COOKIE_NAME, "")
    response = auth.client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": PASSWORD},
        headers=sync_csrf(auth.client),
    )
    assert response.status_code == 200
    assert response.json()["user"]["email_verified"] is False
    second_session = auth.client.cookies.get(SESSION_COOKIE_NAME, "")
    # Rotation: each login must mint a brand new session id (fixation defense).
    assert second_session and second_session != first_session


def test_login_unknown_and_wrong_password_share_one_envelope(auth: Harness) -> None:
    wrong_password = auth.client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": PASSWORD},
        headers=sync_csrf(auth.client),
    )
    unknown = auth.client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": PASSWORD},
        headers=sync_csrf(auth.client),
    )
    assert wrong_password.status_code == unknown.status_code == 401
    assert wrong_password.json() == unknown.json()
    assert wrong_password.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert unknown.json()["error"]["message"] == wrong_password.json()["error"]["message"]


# --- Me ---


def test_me_returns_the_current_user(auth: Harness) -> None:
    signup(auth)
    response = auth.client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"


def test_me_rejects_a_forged_session_cookie(auth: Harness) -> None:
    signup(auth)
    forged = uuid.uuid4().hex * 2
    auth.client.cookies.set(SESSION_COOKIE_NAME, forged)
    response = auth.client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_INVALID"


def test_me_rejects_an_expired_session(auth: Harness, app_engine: Engine) -> None:
    signup(auth)
    with app_engine.begin() as connection:
        connection.execute(
            text("UPDATE sessions SET expires_at = now() - interval '1 minute'")
        )
    response = auth.client.get("/auth/me")
    assert response.status_code == 401


# --- Logout ---


def test_logout_deletes_the_session(auth: Harness) -> None:
    signup(auth)
    token = auth.client.cookies.get(SESSION_COOKIE_NAME, "")
    csrf_token = auth.client.cookies.get(CSRF_COOKIE_NAME, "")
    logout = auth.client.post(
        "/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": csrf_token},
    )
    assert logout.status_code == 200
    # Session row really removed: the remembered token no longer resolves.
    assert auth.client.get("/auth/me").status_code == 401
    assert token not in auth.client.cookies.get(SESSION_COOKIE_NAME, "")


def test_logout_requires_a_session_bound_csrf_pair(auth: Harness) -> None:
    signup(auth)
    mismatched = auth.client.post(
        "/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": "not-the-bound-token"},
    )
    assert mismatched.status_code == 403
    assert (
        mismatched.json()["error"]["code"] == "CSRF_VALIDATION_FAILED"
    )
    # The double-submit pair itself must also stay required.
    pairless = auth.client.post("/auth/logout", headers={"Origin": ORIGIN})
    assert pairless.status_code == 403


def test_refetched_csrf_pair_keeps_the_session_usable(auth: Harness) -> None:
    """A client may safely refetch /csrf mid-session: /csrf re-binds it."""
    signup(auth)
    auth.client.get("/csrf")  # re-binds the session's stored hash
    headers = {
        "Origin": ORIGIN,
        "X-CSRF-Token": auth.client.cookies.get(CSRF_COOKIE_NAME, ""),
    }
    assert auth.client.post("/auth/logout", headers=headers).status_code == 200


def test_a_consistent_pair_that_is_not_bound_is_rejected(auth: Harness) -> None:
    """Same-origin double-submit alone is not enough for a real session.

    The pair is self-consistent (cookie == header), so the middleware passes
    it, but only the session's stored hash decides (WARN-E-006).
    """
    signup(auth)
    stranger_token = generate_token()
    auth.client.cookies.set(CSRF_COOKIE_NAME, stranger_token)
    response = auth.client.post(
        "/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": stranger_token},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CSRF_VALIDATION_FAILED"


def test_logout_requires_a_session(auth: Harness) -> None:
    with TestClient(api_app, base_url="http://testserver") as fresh:
        fresh.get("/csrf")
        response = fresh.post(
            "/auth/logout",
            headers={
                "Origin": ORIGIN,
                "X-CSRF-Token": fresh.cookies.get(CSRF_COOKIE_NAME, ""),
            },
        )
        assert response.status_code == 401


# --- Verification ---


def test_verify_marks_the_user_verified(auth: Harness) -> None:
    signup(auth)
    token = verification_token(auth)
    response = auth.client.get(f"/auth/verify?token={token}")
    assert response.status_code == 200
    assert response.json() == {"email_verified": True}
    assert auth.client.get("/auth/me").json()["email_verified"] is True


def test_verify_rejected_states_share_one_envelope(
    auth: Harness, app_engine: Engine
) -> None:
    invalid = auth.client.get("/auth/verify?token=not-a-real-token")
    assert invalid.status_code == 400
    signup(auth)
    token = verification_token(auth)
    with app_engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE email_verifications"
                " SET expires_at = now() - interval '1 minute'"
            )
        )
    expired_response = auth.client.get(f"/auth/verify?token={token}")
    assert expired_response.status_code == 400
    assert expired_response.json() == invalid.json()


def test_verify_reused_token_fails(auth: Harness) -> None:
    signup(auth)
    token = verification_token(auth)
    first = auth.client.get(f"/auth/verify?token={token}")
    assert first.status_code == 200
    reused = auth.client.get(f"/auth/verify?token={token}")
    assert reused.status_code == 400
    assert reused.json() == auth.client.get("/auth/verify?token=garbage").json()


def test_verify_without_token_fails(auth: Harness) -> None:
    response = auth.client.get("/auth/verify")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VERIFICATION_LINK_INVALID"


# --- Cookie flags ---


def test_session_cookie_is_httponly_and_csrf_cookie_is_readable(auth: Harness) -> None:
    response = signup(auth)
    set_cookies = response.headers.get_list("set-cookie")
    session_cookie = next(
        value for value in set_cookies if value.startswith(f"{SESSION_COOKIE_NAME}=")
    )
    csrf_cookie = next(value for value in set_cookies if value.startswith("csrf_token="))
    assert "HttpOnly" in session_cookie
    assert "Secure" not in session_cookie  # local environments allow plain HTTP
    assert "SameSite=lax" in session_cookie
    assert "HttpOnly" not in csrf_cookie  # the browser JS must read it (SEC-001)
    assert "Path=/" in session_cookie and "Path=/" in csrf_cookie

