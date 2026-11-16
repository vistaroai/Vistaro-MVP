"""AUTH-003: the generated role-to-permission matrix test.

The playbook requires "a generated matrix test covering every role on every
protected route". This module generates that test from two sources:

1. ``vistaro.sentinel.permissions.PROTECTED_ROUTES`` declares every route
   that enforces a permission, and which permission it enforces.
2. The live FastAPI app is inspected to prove the declaration is true. A
   route that enforces a permission but is not declared fails the drift
   check, and a declared route that does not enforce its permission fails
   too. The map can therefore never drift away from the routes again.

Each generated case then acts as a real member of the workspace with one
role, calls the route, and asserts the outcome the permission map predicts:
the route's success status when the role carries the permission, and 403 with
code PERMISSION_DENIED when it does not.
"""

from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from conftest import UserSession
from sqlalchemy import Engine, text

from vistaro.main import app as api_app
from vistaro.sentinel.permissions import (
    ALL_PERMISSIONS,
    PROTECTED_ROUTES,
    ROLE_PERMISSIONS,
    has_permission,
    may_approve,
)

#: The roles the memberships table accepts, in matrix order.
ROLES: tuple[str, ...] = ("owner", "admin", "editor", "approver", "viewer")

#: Signup index of the account that plays each role. Index 0 creates the
#: workspace and is therefore its owner; the rest are inserted as members.
ROLE_ACCOUNT_INDEX: dict[str, int] = {
    "owner": 0,
    "admin": 1,
    "editor": 2,
    "approver": 3,
    "viewer": 4,
}


# --- The generated matrix --------------------------------------------------


def _iter_routes(routes: object, prefix: str = "") -> Iterator[object]:
    """Yield every concrete route, descending into wrapped included routers.

    Recent FastAPI wraps each ``include_router`` in a lazy container instead
    of copying its routes onto the app, so ``app.routes`` alone is not the
    whole route table. The container exposes ``original_router`` (the APIRouter
    that was included) and ``include_context.prefix``.
    """
    for route in routes:  # type: ignore[union-attr]
        included = getattr(route, "original_router", None)
        if included is not None:
            context = getattr(route, "include_context", None)
            included_prefix = getattr(context, "prefix", "") or ""
            yield from _iter_routes(included.routes, prefix + included_prefix)
            continue
        yield route


def _permissions_enforced_by(route: object) -> set[str]:
    """Every permission the route's dependency tree enforces."""
    found: set[str] = set()

    def walk(dependant: object) -> None:
        for dependency in getattr(dependant, "dependencies", []):
            permission = getattr(dependency.call, "permission", None)
            if isinstance(permission, str):
                found.add(permission)
            walk(dependency)

    walk(getattr(route, "dependant", None))
    return found


def _live_permission_map() -> dict[tuple[str, str], set[str]]:
    """(method, path) -> permissions the live app enforces on that route."""
    live: dict[tuple[str, str], set[str]] = {}
    for route in _iter_routes(api_app.routes):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not path or not methods:
            continue
        enforced = _permissions_enforced_by(route)
        if not enforced:
            continue
        for method in methods:
            live[(method.upper(), path)] = enforced
    return live


@dataclass(frozen=True)
class Matrix:
    """The workspace the matrix runs against, plus one handle per role."""

    workspace_id: str
    sessions: dict[str, UserSession]
    target_emails: dict[str, str]


@pytest.fixture(name="matrix")
def fixture_matrix(
    signed_up_users: list[UserSession], admin_engine: Engine
) -> Iterator[Matrix]:
    """One workspace with one member per role, plus an add-member target."""
    owner = signed_up_users[0]
    created = owner.post("/workspaces", {"name": "Matrix Workspace"})
    assert created.status_code == 201, created.json()  # type: ignore[attr-defined]
    workspace_id = str(created.json()["id"])  # type: ignore[attr-defined]

    with admin_engine.begin() as connection:
        for role, index in ROLE_ACCOUNT_INDEX.items():
            if role == "owner":
                continue  # the creator already holds the owner membership
            email = signed_up_users[index].email
            user_id = connection.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email},
            ).scalar_one()
            connection.execute(
                text(
                    "INSERT INTO memberships (workspace_id, user_id, role)"
                    " VALUES (:wid, :uid, :role)"
                ),
                {"wid": workspace_id, "uid": str(user_id), "role": role},
            )
        # Target accounts for the add-member route. They only have to exist:
        # add_member looks the email up in users and grants the role, it never
        # authenticates the target. Inserted directly rather than signed up
        # because signup costs an Argon2id hash per case.
        targets = {role: f"target-{role}@example.com" for role in ROLES}
        for email in targets.values():
            connection.execute(
                text(
                    "INSERT INTO users (id, email, password_hash)"
                    " VALUES (gen_random_uuid(), :email, 'matrix-target')"
                ),
                {"email": email},
            )

    sessions = {
        role: signed_up_users[index] for role, index in ROLE_ACCOUNT_INDEX.items()
    }
    yield Matrix(workspace_id=workspace_id, sessions=sessions, target_emails=targets)


def _call(route_spec: object, matrix: Matrix, role: str) -> object:
    """Invoke one protected route as the member holding *role*."""
    session = matrix.sessions[role]
    path = route_spec.path.format(workspace_id=matrix.workspace_id)  # type: ignore[attr-defined]
    if route_spec.method == "GET":  # type: ignore[attr-defined]
        return session.get(path)
    if route_spec.path.endswith("/switch"):  # type: ignore[attr-defined]
        return session.post(path)
    return session.post(
        path,
        {"email": matrix.target_emails[role], "role": "editor"},
    )


def _build_matrix_case(
    route_spec: object, role: str
) -> "callable[[Matrix], None]":
    """Build one generated test case for a (route, role) pair."""

    def case(matrix: Matrix) -> None:
        response = _call(route_spec, matrix, role)
        allowed = has_permission(role, route_spec.permission)  # type: ignore[attr-defined]
        if allowed:
            assert response.status_code == route_spec.success_status, (  # type: ignore[attr-defined]
                f"{role} holds {route_spec.permission} but the route answered "  # type: ignore[attr-defined]
                f"{response.status_code}"
            )
        else:
            assert response.status_code == 403, (  # type: ignore[attr-defined]
                f"{role} lacks {route_spec.permission} but the route answered "  # type: ignore[attr-defined]
                f"{response.status_code}"
            )
            assert response.json()["error"]["code"] == "PERMISSION_DENIED"  # type: ignore[attr-defined]

    return case


#: One generated test per (protected route, role) pair.
MATRIX_CASES: list[tuple[object, str]] = [
    (route_spec, role) for route_spec in PROTECTED_ROUTES for role in ROLES
]


@pytest.mark.parametrize(
    ("route_spec", "role"),
    MATRIX_CASES,
    ids=[
        f"{route_spec.method.lower()}-{route_spec.path}-{role}"
        for route_spec, role in MATRIX_CASES
    ],
)
def test_permission_matrix(
    route_spec: object, role: str, matrix: Matrix
) -> None:
    """Every role against every protected route."""
    _build_matrix_case(route_spec, role)(matrix)


# --- Drift checks ----------------------------------------------------------


def test_declared_routes_match_the_live_app() -> None:
    """The registry and the live app enforce exactly the same permissions."""
    live = _live_permission_map()
    declared = {
        (route_spec.method.upper(), route_spec.path): {route_spec.permission}
        for route_spec in PROTECTED_ROUTES
    }
    assert declared == live


def test_every_map_permission_is_declared_or_known() -> None:
    """The map never invents a permission outside the known set."""
    for role, permissions in ROLE_PERMISSIONS.items():
        assert permissions <= ALL_PERMISSIONS, (
            f"role '{role}' carries unknown permissions: "
            f"{sorted(permissions - ALL_PERMISSIONS)}"
        )


def test_map_roles_match_the_database_check_constraint(
    admin_engine: Engine,
) -> None:
    """The map knows exactly the roles the memberships table accepts."""
    with admin_engine.connect() as connection:
        definition = connection.execute(
            text(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint"
                " WHERE conrelid = 'memberships'::regclass AND contype = 'c'"
            )
        ).scalar_one()
    assert definition is not None
    for role in ROLES:
        assert f"'{role}'" in definition
    assert set(ROLE_PERMISSIONS) == set(ROLES)


def test_unknown_role_carries_no_permission() -> None:
    """A role the map does not know about fails closed."""
    assert has_permission("superuser", "workspace.read") is False
    assert has_permission("", "members.add") is False


# --- The approver rule ----------------------------------------------------


def test_only_owner_admin_and_approver_may_approve() -> None:
    """The map's approvers are exactly owner, admin and approver."""
    for role in ROLES:
        expected = role in ("owner", "admin", "approver")
        assert (
            may_approve(
                actor_user_id="actor",
                actor_role=role,
                requester_user_id="someone-else",
                agent_initiated=True,
            )
            is expected
        ), role


def test_requester_cannot_approve_own_agent_request() -> None:
    """An agent-initiated request needs a different person to approve it."""
    assert (
        may_approve(
            actor_user_id="same",
            actor_role="owner",
            requester_user_id="same",
            agent_initiated=True,
        )
        is False
    )
    assert (
        may_approve(
            actor_user_id="same",
            actor_role="admin",
            requester_user_id="same",
            agent_initiated=True,
        )
        is False
    )
    # A human may approve a request they raised themselves.
    assert (
        may_approve(
            actor_user_id="same",
            actor_role="owner",
            requester_user_id="same",
            agent_initiated=False,
        )
        is True
    )


def test_approver_role_may_approve_own_agent_request() -> None:
    """Holding the approver role is what lifts the self-approval ban."""
    assert (
        may_approve(
            actor_user_id="same",
            actor_role="approver",
            requester_user_id="same",
            agent_initiated=True,
        )
        is True
    )
