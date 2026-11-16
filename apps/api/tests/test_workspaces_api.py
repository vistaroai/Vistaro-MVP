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
from conftest import UserSession
from sqlalchemy import Engine, text


@pytest.fixture(name="ws")
def fixture_ws(signed_up_users: list[UserSession]) -> Iterator[dict[str, UserSession]]:
    """Two account handles on one TestClient: 'a' creates, 'b' is invited."""
    yield {"a": signed_up_users[0], "b": signed_up_users[1]}


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
        denied.json()["error"]["code"] == "PERMISSION_DENIED"  # type: ignore[attr-defined]
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
