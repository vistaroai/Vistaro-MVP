"""AUTH-002 API tests: workspaces, switching, members, tenant scoping.

Runs the real app against the real Postgres as the app role, so RLS (both
the workspace and the new user branch) is exercised by the same paths the
production endpoints take. One TestClient (one lifespan/loop) serves BOTH
accounts by explicitly swapping the two cookies per request; a fixture with
two nested TestClients would double-run the app lifespan and break the
shared async Redis client's event-loop binding.
"""

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from vistaro.api.deps import SESSION_COOKIE_NAME
from vistaro.core.security import CSRF_COOKIE_NAME
from vistaro.main import app as api_app

ORIGIN = "http://localhost:5173"
PASSWORD = "correct-horse-battery-staple"


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


@pytest.fixture(name="ws")
def fixture_ws(
    app_engine: Engine, admin_engine: Engine
) -> Iterator[dict[str, UserSession]]:
    """Fresh account tables; yields two account handles on one TestClient."""
    with admin_engine.begin() as connection:
        connection.execute(
            text("TRUNCATE sessions, email_verifications, users CASCADE")
        )
    try:
        with TestClient(app=api_app, base_url="http://testserver") as client:
            a = UserSession(client, "user-0@example.com")
            b = UserSession(client, "user-1@example.com")
            for session in (a, b):
                session.signup()
            yield {"a": a, "b": b}
    finally:
        with admin_engine.begin() as connection:
            connection.execute(
                text("TRUNCATE sessions, email_verifications, users CASCADE")
            )


def create_workspace(handle: UserSession, name: str) -> dict[str, object]:
    """Create one workspace, asserting success."""
    response = handle.post("/workspaces", {"name": name})
    assert response.status_code == 201, response.json()  # type: ignore[attr-defined]
    return response.json()  # type: ignore[attr-defined, return-value]


# --- Create and list ---


def test_created_workspace_lists_for_its_owner(
    ws: dict[str, UserSession],
) -> None:
    created = create_workspace(ws["a"], "Alpha Labs")
    listing = ws["a"].get("/workspaces").json()["workspaces"]  # type: ignore[attr-defined]
    assert [entry["id"] for entry in listing] == [created["id"]]
    assert created["role"] == "owner"
    assert created["name"] == "Alpha Labs"


def test_second_user_sees_no_one_elses_workspaces(
    ws: dict[str, UserSession],
) -> None:
    create_workspace(ws["a"], "Alpha Labs")
    listing = ws["b"].get("/workspaces")  # type: ignore[attr-defined]
    assert listing.status_code == 200  # type: ignore[attr-defined]
    assert listing.json()["workspaces"] == []  # type: ignore[attr-defined]


def test_workspace_name_is_validated(ws: dict[str, UserSession]) -> None:
    blank = ws["a"].post("/workspaces", {"name": "   "})  # type: ignore[attr-defined]
    assert blank.status_code == 422  # type: ignore[attr-defined]


# --- Switch ---


def test_switch_updates_the_session_row(
    ws: dict[str, UserSession], app_engine: Engine
) -> None:
    create_workspace(ws["a"], "Alpha")
    second = create_workspace(ws["a"], "Beta")
    switch = ws["a"].post(f"/workspaces/{second['id']}/switch")  # type: ignore[attr-defined]
    assert switch.status_code == 200  # type: ignore[attr-defined]
    assert switch.json()["id"] == second["id"]  # type: ignore[attr-defined]
    assert switch.json()["role"] == "owner"  # type: ignore[attr-defined]

    with app_engine.connect() as connection:
        active = connection.execute(
            text(
                "SELECT count(*) FROM sessions WHERE active_workspace_id = :wid"
            ),
            {"wid": second["id"]},
        ).scalar_one()
    assert active == 1


def test_switch_to_unknown_or_foreign_workspace_is_404(
    ws: dict[str, UserSession],
) -> None:
    create_workspace(ws["a"], "Alpha")  # B is NOT a member here
    response = ws["b"].post(f"/workspaces/{uuid.uuid4()}/switch")  # type: ignore[attr-defined]
    assert response.status_code == 404  # type: ignore[attr-defined]
    assert (
        response.json()["error"]["code"] == "WORKSPACE_NOT_FOUND"  # type: ignore[attr-defined]
    )


def test_member_of_two_workspaces_can_switch(
    ws: dict[str, UserSession],
) -> None:
    """B joins A's workspace via add-member, then switches into it."""
    created = create_workspace(ws["a"], "Alpha")
    add = ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "editor"},
    )
    assert add.status_code == 201  # type: ignore[attr-defined]
    switch = ws["b"].post(f"/workspaces/{created['id']}/switch")  # type: ignore[attr-defined]
    assert switch.status_code == 200  # type: ignore[attr-defined]
    assert switch.json()["role"] == "editor"  # type: ignore[attr-defined]
    listing = ws["b"].get("/workspaces").json()["workspaces"]  # type: ignore[attr-defined]
    assert len(listing) == 1
    assert listing[0]["id"] == created["id"]


# --- Members ---


def test_owner_adds_member_and_sees_both(
    ws: dict[str, UserSession],
) -> None:
    created = create_workspace(ws["a"], "Alpha")
    add = ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "editor"},
    )
    assert add.status_code == 201  # type: ignore[attr-defined]
    members = {  # type: ignore[attr-defined]
        entry["email"]: entry["role"] for entry in add.json()["members"]
    }
    assert members == {
        "user-0@example.com": "owner",
        "user-1@example.com": "editor",
    }


def test_member_add_requires_owner_or_admin(
    ws: dict[str, UserSession],
) -> None:
    created = create_workspace(ws["a"], "Alpha")
    ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "editor"},
    )
    denied = ws["b"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-0@example.com", "role": "viewer"},
    )
    assert denied.status_code == 403  # type: ignore[attr-defined]
    assert (
        denied.json()["error"]["code"] == "MEMBER_ADD_NOT_ALLOWED"  # type: ignore[attr-defined]
    )


def test_member_add_rejects_owner_role_and_unknown_email(
    ws: dict[str, UserSession],
) -> None:
    created = create_workspace(ws["a"], "Alpha")
    owner_grant = ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "owner"},
    )
    assert owner_grant.status_code == 422  # type: ignore[attr-defined]
    unknown = ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "ghost@example.com", "role": "editor"},
    )
    assert unknown.status_code == 404  # type: ignore[attr-defined]
    assert unknown.json()["error"]["code"] == "USER_NOT_FOUND"  # type: ignore[attr-defined]


def test_duplicate_member_is_409(ws: dict[str, UserSession]) -> None:
    created = create_workspace(ws["a"], "Alpha")
    add = ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "viewer"},
    )
    assert add.status_code == 201  # type: ignore[attr-defined]
    again = ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "editor"},
    )
    assert again.status_code == 409  # type: ignore[attr-defined]
    assert (
        again.json()["error"]["code"]  # type: ignore[attr-defined]
        == "MEMBER_ALREADY_IN_WORKSPACE"
    )


def test_member_lists_members_but_outsider_gets_404(
    ws: dict[str, UserSession],
) -> None:
    created = create_workspace(ws["a"], "Alpha")
    ws["a"].post(  # type: ignore[attr-defined]
        f"/workspaces/{created['id']}/members",
        {"email": "user-1@example.com", "role": "editor"},
    )
    member_view = ws["b"].get(f"/workspaces/{created['id']}/members")  # type: ignore[attr-defined]
    assert member_view.status_code == 200  # type: ignore[attr-defined]
    assert len(member_view.json()["members"]) == 2  # type: ignore[attr-defined]

    private = create_workspace(ws["b"], "Private Beta")
    response = ws["a"].get(f"/workspaces/{private['id']}/members")  # type: ignore[attr-defined]
    assert response.status_code == 404  # type: ignore[attr-defined]
    assert (
        response.json()["error"]["code"] == "WORKSPACE_NOT_FOUND"  # type: ignore[attr-defined]
    )
