"""Shared fixtures for database-backed tests (TEST-001).

Also holds the signed-in session helper the API test modules share. One
TestClient serves every account in a test by explicitly swapping the cookies
per request: a fixture with two nested TestClients would double-run the app
lifespan and break the shared async Redis client's event-loop binding.
"""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

# Auth flow tests fire many POSTs through the real app's limiter; lift the
# per-peer limit for the whole test process. Threshold behavior itself is
# tested separately in test_security with a dedicated mini-app and explicit
# constructor arguments, so this override does not weaken any test.
os.environ["RATE_LIMIT_REQUESTS"] = "100000"

from vistaro.api.deps import SESSION_COOKIE_NAME  # noqa: E402
from vistaro.core.config import settings  # noqa: E402
from vistaro.core.security import CSRF_COOKIE_NAME  # noqa: E402
from vistaro.db.tenancy import admin_database_url, build_engine  # noqa: E402
from vistaro.main import app as api_app  # noqa: E402

WORKSPACE_A_ID: Final[str] = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
WORKSPACE_B_ID: Final[str] = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
USER_A_ID: Final[str] = "11111111-1111-1111-1111-111111111111"
USER_B_ID: Final[str] = "22222222-2222-2222-2222-222222222222"

#: Origin the CSRF middleware accepts in tests.
ORIGIN: Final[str] = "http://localhost:5173"
#: Password used by every test account.
PASSWORD: Final[str] = "correct-horse-battery-staple"

TRUNCATE_ALL_SQL: Final = (
    "TRUNCATE sessions, memberships, workspaces, users, email_verifications CASCADE"
)


class UserSession:
    """One account's cookie pair over the single shared TestClient."""

    def __init__(self, client: TestClient, email: str) -> None:
        self.client = client
        self.email = email
        self.session_token: str = ""
        self.csrf_token: str = ""

    def _apply_cookies(self) -> None:
        # Clearing prevents duplicate cookies; empty domain because httpx's
        # default policy rejects a named domain for a dotless test host.
        self.client.cookies.clear()
        self.client.cookies.set(
            SESSION_COOKIE_NAME, self.session_token, domain="", path="/"
        )
        self.client.cookies.set(
            CSRF_COOKIE_NAME, self.csrf_token, domain="", path="/"
        )

    def refresh_csrf(self) -> None:
        """Fetch a fresh CSRF pair bound to THIS session only."""
        self._apply_cookies()
        response = self.client.get("/csrf")
        assert response.status_code == 200, response.text
        token = response.json()["csrf_token"]
        # Response sets the CSRF cookie; read the value back from the jar
        # because re-binding always pairs cookie with header.
        self.csrf_token = token

    def signup(self) -> None:
        """Register the account and keep its session + CSRF tokens."""
        self.client.cookies.clear()
        csrf = self.client.get("/csrf").json()["csrf_token"]
        response = self.client.post(
            "/auth/signup",
            json={"email": self.email, "password": PASSWORD},
            headers={"Origin": ORIGIN, "X-CSRF-Token": csrf},
        )
        assert response.status_code == 201, response.text
        self.session_token = str(self.client.cookies.get(SESSION_COOKIE_NAME))
        self.refresh_csrf()  # binds to this new session

    def get(self, path: str) -> object:
        self._apply_cookies()
        return self.client.get(path)

    def post(self, path: str, json: object = None) -> object:
        self._apply_cookies()
        headers = {"Origin": ORIGIN, "X-CSRF-Token": self.csrf_token}
        return self.client.post(path, json=json, headers=headers)


@pytest.fixture(name="app_client")
def fixture_app_client() -> Iterator[TestClient]:
    """One TestClient for the whole test, so the app lifespan runs once."""
    with TestClient(app=api_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(name="signed_up_users")
def fixture_signed_up_users(
    app_client: TestClient, admin_engine: Engine
) -> Iterator[list[UserSession]]:
    """Empty user tables, then sign up one account per requested email.

    Yields the sessions in the order the emails were requested. The tables are
    truncated again afterwards, so tests never see another test's accounts.
    """
    with admin_engine.begin() as connection:
        connection.execute(text(TRUNCATE_ALL_SQL))
    try:
        sessions = [UserSession(app_client, email) for email in SIGNUP_EMAILS]
        for session in sessions:
            session.signup()
        yield sessions
    finally:
        with admin_engine.begin() as connection:
            connection.execute(text(TRUNCATE_ALL_SQL))


#: Emails the signed_up_users fixture registers. Index 0 creates workspaces;
#: the rest are members that the permission matrix assigns roles to.
SIGNUP_EMAILS: Final[tuple[str, ...]] = (
    "user-0@example.com",
    "user-1@example.com",
    "user-2@example.com",
    "user-3@example.com",
    "user-4@example.com",
)


@dataclass(frozen=True)
class TwoWorkspaces:
    """Seeded fixture data: two workspaces with one owner membership each."""

    workspace_a: str = WORKSPACE_A_ID
    workspace_b: str = WORKSPACE_B_ID
    user_a: str = USER_A_ID
    user_b: str = USER_B_ID


@pytest.fixture(name="admin_engine")
def fixture_admin_engine() -> Iterator[Engine]:
    """Superuser engine used only to seed and clean fixtures."""
    try:
        engine = build_engine(admin_database_url())
        with engine.connect() as probe:
            probe.execute(text("SELECT 1"))
    except Exception as error:  # noqa: BLE001 - surface the real reason
        pytest.skip(f"database is not reachable: {error}")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(name="app_engine")
def fixture_app_engine() -> Iterator[Engine]:
    """Engine connecting exactly as the application role (vistaro_app)."""
    engine = build_engine(settings.database_url)
    try:
        yield engine
    finally:
        engine.dispose()


def _seed_two_workspaces(engine: Engine) -> None:
    """Seed one owner membership per workspace; bypasses RLS as required."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (id, email, password_hash)"
                " VALUES (:user_a, 'owner-a@example.test', 'seed'),"
                " (:user_b, 'owner-b@example.test', 'seed')"
            ),
            {"user_a": USER_A_ID, "user_b": USER_B_ID},
        )
        connection.execute(
            text(
                "INSERT INTO workspaces (id, name, created_by)"
                " VALUES (:ws_a, 'Workspace A', :user_a),"
                " (:ws_b, 'Workspace B', :user_b)"
            ),
            {
                "ws_a": WORKSPACE_A_ID,
                "ws_b": WORKSPACE_B_ID,
                "user_a": USER_A_ID,
                "user_b": USER_B_ID,
            },
        )
        connection.execute(
            text(
                "INSERT INTO memberships (workspace_id, user_id, role)"
                " VALUES (:ws_a, :user_a, 'owner'), (:ws_b, :user_b, 'owner')"
            ),
            {
                "ws_a": WORKSPACE_A_ID,
                "ws_b": WORKSPACE_B_ID,
                "user_a": USER_A_ID,
                "user_b": USER_B_ID,
            },
        )


@pytest.fixture(name="two_workspaces")
def fixture_two_workspaces(admin_engine: Engine) -> Iterator[TwoWorkspaces]:
    """Remove any leftovers, seed two isolated workspaces, remove again after."""
    with admin_engine.begin() as connection:
        connection.execute(text(TRUNCATE_ALL_SQL))
    _seed_two_workspaces(admin_engine)
    try:
        yield TwoWorkspaces()
    finally:
        with admin_engine.begin() as connection:
            connection.execute(text(TRUNCATE_ALL_SQL))
