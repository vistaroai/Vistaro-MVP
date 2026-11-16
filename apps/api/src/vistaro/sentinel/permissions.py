"""Sentinel permission map - the single source of role-to-permission truth.

AUTH-003. This module is the ONLY place that maps roles to the permissions
that guard workspace-scoped routes. Every protected route declares its
permission through the PROTECTED_ROUTES registry below and enforces it with
the require_permission dependency in vistaro.api.deps, which calls require()
here. SEN-001 extends this map; it must not add a second source of role truth
(WARN-B-001, WARN-B-006).

The matrix is finite on purpose: adding a permission entry only adds
capability, it never silently removes one.

Role matrix (approved 2026-11-16):

| Role        | Permissions |
| ----------- | ----------- |
| owner       | every permission |
| admin       | read + members.add + approvals |
| editor      | read + approvals.request |
| approver    | read + approvals.request + approvals.approve |
| viewer      | read + approvals.request |

Read means workspace.read, workspace.switch and members.read: every member of
a workspace can read it, list its members and switch into it. That matches the
behaviour AUTH-002 already shipped and its tests assert, so AUTH-003
formalizes it rather than changing it.
"""

from dataclasses import dataclass

from vistaro.core.errors import ForbiddenError

# --- Permission names ------------------------------------------------------

WORKSPACE_READ = "workspace.read"
WORKSPACE_SWITCH = "workspace.switch"
MEMBERS_READ = "members.read"
MEMBERS_ADD = "members.add"
MEMBERS_REMOVE = "members.remove"
APPROVALS_REQUEST = "approvals.request"
APPROVALS_APPROVE = "approvals.approve"

#: Every permission the product knows about. The map below must not invent
#: permissions outside this set.
ALL_PERMISSIONS: frozenset[str] = frozenset(
    {
        WORKSPACE_READ,
        WORKSPACE_SWITCH,
        MEMBERS_READ,
        MEMBERS_ADD,
        MEMBERS_REMOVE,
        APPROVALS_REQUEST,
        APPROVALS_APPROVE,
    }
)

#: The role a membership must hold to approve an agent-initiated request that
#: the same person raised (ARCHITECTURE section 5, "Approvers").
APPROVER_ROLE = "approver"

# --- The map ---------------------------------------------------------------

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "owner": frozenset(ALL_PERMISSIONS),
    "admin": frozenset(
        {
            WORKSPACE_READ,
            WORKSPACE_SWITCH,
            MEMBERS_READ,
            MEMBERS_ADD,
            APPROVALS_REQUEST,
            APPROVALS_APPROVE,
        }
    ),
    "editor": frozenset(
        {WORKSPACE_READ, WORKSPACE_SWITCH, MEMBERS_READ, APPROVALS_REQUEST}
    ),
    "approver": frozenset(
        {
            WORKSPACE_READ,
            WORKSPACE_SWITCH,
            MEMBERS_READ,
            APPROVALS_REQUEST,
            APPROVALS_APPROVE,
        }
    ),
    "viewer": frozenset(
        {WORKSPACE_READ, WORKSPACE_SWITCH, MEMBERS_READ, APPROVALS_REQUEST}
    ),
}


def has_permission(role: str, permission: str) -> bool:
    """Return True iff role carries permission according to the map.

    An unknown role carries nothing. That fails closed: a membership row with
    a role the map does not know about can never pass a permission check.
    """
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def require(user: str, action: str, workspace: str | None = None) -> None:
    """Enforce that the caller's role carries action; raise ForbiddenError.

    Mirrors the architecture's sentinel.permissions.require(user, action,
    workspace) call shape. "user" is the caller's role in "workspace"; the
    workspace id is recorded for auditability only, it does not change the
    decision.

    Raises ForbiddenError (HTTP 403, code PERMISSION_DENIED) when the role
    does not carry the action.
    """
    if has_permission(user, action):
        return
    raise ForbiddenError(
        f"Role '{user}' may not perform '{action}'."
        + (f" (workspace {workspace})" if workspace else "")
    )


def may_approve(
    *,
    actor_user_id: str,
    actor_role: str,
    requester_user_id: str,
    agent_initiated: bool,
) -> bool:
    """The approver rule from ARCHITECTURE section 5.

    Only owner, admin and approver may approve at all. A requester may not
    approve their own agent-initiated request unless they hold the approver
    role; that is the separation of duties the rule exists for. A request
    raised by a human is approvable by that same human, because nothing
    automated is riding on it.

    SEN-001 calls this when an approval decision is recorded.
    """
    if not has_permission(actor_role, APPROVALS_APPROVE):
        return False
    if agent_initiated and actor_user_id == requester_user_id:
        return actor_role == APPROVER_ROLE
    return True


# --- Protected route registry ---------------------------------------------


@dataclass(frozen=True)
class ProtectedRoute:
    """One route that enforces a permission, and what it expects on success.

    The registry is the source of truth for the generated matrix test: the
    test walks every entry against every role, and also asserts that the
    live FastAPI app enforces exactly this permission on exactly these
    routes. A route added without a registry entry fails the drift check, and
    a registry entry with no matching route fails too.
    """

    method: str
    path: str
    permission: str
    success_status: int


PROTECTED_ROUTES: tuple[ProtectedRoute, ...] = (
    ProtectedRoute(
        method="GET",
        path="/workspaces/{workspace_id}/members",
        permission=WORKSPACE_READ,
        success_status=200,
    ),
    ProtectedRoute(
        method="POST",
        path="/workspaces/{workspace_id}/switch",
        permission=WORKSPACE_READ,
        success_status=200,
    ),
    ProtectedRoute(
        method="POST",
        path="/workspaces/{workspace_id}/members",
        permission=MEMBERS_ADD,
        success_status=201,
    ),
)
