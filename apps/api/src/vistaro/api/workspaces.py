"""AUTH-002: workspaces, switching, and members.

Design contract:
- Every query runs through ``tenant_session`` (or an explicitly scoped
  connection), so RLS-GUC scoping cannot be forgotten: ``app.user_id`` always
  (from the verified session), ``app.workspace_id`` when the workspace is
  known. RLS stays the second layer after application filters (ADR-005).
- Membership truth is the database: the shared ``WorkspaceContextDep``
  resolves the path workspace from the caller's live membership, and a
  nonexistent or foreign workspace answers the same generic 404
  (``WORKSPACE_NOT_FOUND``) either way — no existence leaks.
- Switching stores the workspace on the session row (sessions are user-scoped
  by code and digest, WARN-D-007); switching does NOT change identity, so the
  session id and CSRF binding stay intact.
- Member management (AUTH-003 formalizes the full role/permission map): the
  MVP rule is owner/admin may add members; the ``owner`` role itself is not
  assignable here. Added by email; unknown email answers 404, which
  explicitly reveals account existence to trusted workspace admins (signup
  already answers 409) — the email-invite-token flow can replace this if the
  founders prefer no such leak.

Sessions and memberships are the tenant tables touched; the registry
``TENANT_TABLE_WORKSPACE_COLUMNS`` already covers memberships (TEST-001).
"""

import uuid
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import text

from vistaro.api.deps import (
    CurrentUser,
    WorkspaceContextDep,
    _session_engine,
)
from vistaro.core.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from vistaro.db.tenancy import set_tenant_scope, set_user_scope, tenant_session

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

#: Roles assignable by the add-member endpoint. ``owner`` is deliberately
#: excluded until AUTH-003 formalizes the role/permission map.
ASSIGNABLE_ROLES = ("admin", "editor", "approver", "viewer")


class WorkspaceCreate(BaseModel):
    """Payload: the new workspace's display name."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        """Trim and reject whitespace-only or control-character names."""
        trimmed = value.strip()
        if any(character in "\x00\r\n" for character in trimmed):
            raise ValueError("Name must not contain control characters")
        if not trimmed:
            raise ValueError("Name must not be empty")
        return trimmed


class WorkspaceOut(BaseModel):
    """A workspace plus the caller's role in it."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    role: str
    created_at: datetime


class WorkspaceList(BaseModel):
    """All workspaces the caller belongs to."""

    model_config = ConfigDict(extra="forbid")

    workspaces: list[WorkspaceOut]


class WorkspaceMember(BaseModel):
    """One member of a workspace (emails are shared with co-members)."""

    model_config = ConfigDict(extra="forbid")

    user_id: str
    email: str
    role: str


class MemberList(BaseModel):
    """All members of the workspace."""

    model_config = ConfigDict(extra="forbid")

    members: list[WorkspaceMember]


class AddMemberRequest(BaseModel):
    """Payload: the account email plus the role to grant."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    role: str = "editor"

    @field_validator("role")
    @classmethod
    def assignable_role(cls, value: str) -> str:
        """Reject roles that are outside the MVP-assignable set."""
        if value not in ASSIGNABLE_ROLES:
            raise ValueError(f"role must be one of: {', '.join(ASSIGNABLE_ROLES)}")
        return value


@router.post(
    "",
    status_code=201,
    summary="Create a workspace (creator becomes owner)",
)
def create_workspace(
    user: CurrentUser, request_data: WorkspaceCreate
) -> WorkspaceOut:
    """Create the workspace and one owner membership in one transaction.

    The membership INSERT is gated by RLS ``WITH CHECK``: the transaction's
    workspace GUC is therefore set to the NEW id before the insert, proving
    the same policy future member-grants rely on.
    """
    workspace_id = uuid.uuid4()
    parameters = {
        "id": workspace_id,
        "name": request_data.name,
        "created_by": user.user_id,
    }
    with tenant_session(
        _session_engine(), user_id=user.user_id, workspace_id=str(workspace_id)
    ) as connection:
        connection.execute(
            text(
                "INSERT INTO workspaces (id, name, created_by, created_at)"
                " VALUES (:id, :name, :created_by, now())"
            ),
            parameters,
        )
        connection.execute(
            text(
                "INSERT INTO memberships (workspace_id, user_id, role)"
                " VALUES (:id, :uid, 'owner')"
            ),
            {"id": str(workspace_id), "uid": user.user_id},
        )
        created_at_str = connection.execute(
            text("SELECT created_at FROM workspaces WHERE id = :id"),
            {"id": str(workspace_id)},
        ).scalar_one()
    return WorkspaceOut(
        id=str(workspace_id),
        name=request_data.name,
        role="owner",
        created_at=created_at_str,
    )


@router.get(
    "",
    summary="List the workspaces I belong to",
)
def list_workspaces(user: CurrentUser) -> WorkspaceList:
    """List every workspace the caller has a membership row for.

    Runs with only the user GUC: RLS's user branch scopes the read, so the
    caller sees exactly their own memberships even though the query has no
    explicit workspace filter.
    """
    with _session_engine().connect() as connection:
        set_user_scope(connection, user.user_id)
        rows = connection.execute(
            text(
                "SELECT m.workspace_id, m.role, w.name, w.created_at"
                " FROM memberships m JOIN workspaces w ON w.id = m.workspace_id"
                " ORDER BY w.created_at, w.id"
            )
        ).mappings().all()
    return WorkspaceList(
        workspaces=[
            WorkspaceOut(
                id=str(row["workspace_id"]),
                name=str(row["name"]),
                role=str(row["role"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]
    )


@router.post(
    "/{workspace_id}/switch",
    summary="Make this workspace the session's active workspace",
)
def switch_workspace(
    workspace_id: UUID, user: CurrentUser
) -> WorkspaceOut:
    """Set ``sessions.active_workspace_id`` for the current session.

    Requires a live membership (resolved in the same transaction as the
    update, so a race cannot grant a stale role). Non-members and
    nonexistent workspaces return the same 404 as the context dependency.
    The workspace becomes effective for FUTURE requests in this session.
    """
    with tenant_session(_session_engine(), user_id=user.user_id) as connection:
        membership = connection.execute(
            text(
                "SELECT role, w.name, w.created_at"
                " FROM memberships m JOIN workspaces w ON w.id = m.workspace_id"
                " WHERE m.workspace_id = :wid AND m.user_id = :uid"
            ),
            {"wid": str(workspace_id), "uid": user.user_id},
        ).mappings().first()
        if membership is None:
            raise NotFoundError(
                "Workspace not found", code="WORKSPACE_NOT_FOUND"
            )
        connection.execute(
            text(
                "UPDATE sessions SET active_workspace_id = :wid"
                " WHERE id_hash = :id_hash AND user_id = :uid"
            ),
            {
                "wid": str(workspace_id),
                "id_hash": user.session_id_hash,
                "uid": user.user_id,
            },
        )
    return WorkspaceOut(
        id=str(workspace_id),
        name=str(membership["name"]),
        role=str(membership["role"]),
        created_at=membership["created_at"],
    )


@router.get(
    "/{workspace_id}/members",
    summary="List the workspace's members",
    responses={404: {"description": "Not a member (generic, no existence leak)"}},
)
def list_members(context: WorkspaceContextDep) -> MemberList:
    """List members of a workspace the caller belongs to.

    Other members' emails are shared with co-members by design (collaboration
    surface); flagged for the founders in the review notes.
    """
    return _list_members_of(context.workspace_id)


def _list_members_of(workspace_id: str) -> MemberList:
    """Scoped member listing: the workspace GUC makes RLS do the filtering."""
    with _session_engine().connect() as connection:
        set_tenant_scope(connection, workspace_id)
        rows = connection.execute(
            text(
                "SELECT m.user_id, u.email, m.role FROM memberships m"
                " JOIN users u ON u.id = m.user_id"
                " ORDER BY CASE m.role WHEN 'owner' THEN 0 ELSE 1 END, u.email"
            )
        ).mappings().all()
    return MemberList(
        members=[
            WorkspaceMember(
                user_id=str(row["user_id"]),
                email=str(row["email"]),
                role=str(row["role"]),
            )
            for row in rows
        ]
    )


@router.post(
    "/{workspace_id}/members",
    status_code=201,
    summary="Add a member (owner/admin only; AUTH-003 formalizes permissions)",
    responses={409: {"description": "Already a member"}},
)
def add_member(
    context: WorkspaceContextDep, request_data: AddMemberRequest
) -> MemberList:
    """Grant a role to an existing account within the caller's workspace.

    Authorization (MVP rule): the actor needs the ``owner`` or ``admin``
    role. The INSERT runs with the workspace GUC set, so RLS WITH CHECK
    would reject a cross-workspace grant even if authorization regressed.
    Returns the full member list so the client stays consistent.
    """
    if context.role not in ("owner", "admin"):
        raise ForbiddenError(
            "Only owners and admins can add members",
            code="MEMBER_ADD_NOT_ALLOWED",
        )
    with tenant_session(
        _session_engine(),
        user_id=context.user_id,
        workspace_id=context.workspace_id,
    ) as connection:
        target = connection.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": request_data.email},
        ).mappings().first()
        if target is None:
            raise NotFoundError("No account with that email", code="USER_NOT_FOUND")
        already = connection.execute(
            text(
                "SELECT 1 FROM memberships WHERE workspace_id = :wid AND user_id = :uid"
            ),
            {"wid": context.workspace_id, "uid": str(target["id"])},
        ).first()
        if already is not None:
            raise ConflictError(
                "That account is already a member",
                code="MEMBER_ALREADY_IN_WORKSPACE",
            )
        connection.execute(
            text(
                "INSERT INTO memberships (workspace_id, user_id, role)"
                " VALUES (:wid, :uid, :role)"
            ),
            {
                "wid": context.workspace_id,
                "uid": str(target["id"]),
                "role": request_data.role,
            },
        )
    return _list_members_of(context.workspace_id)
