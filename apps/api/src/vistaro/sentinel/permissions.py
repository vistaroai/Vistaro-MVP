"""Sentinel permission map - single source of role-to-permission assignments (AUTH-003).

This file is the *only* place that maps roles to the permissions that guard
workspace-scoped routes.  Every route that requires authorization should use
``require_permission`` (FastAPI ``Depends``) rather than ad-hoc ``if`` checks,
so that SEN-001 can extend the map without re-wiring each route.

The matrix below is deliberately finite: adding a new permission entry never
silently breaks existing routes; it only adds capability.  Future namespaces
are documented in comments so the map can grow predictably.
"""

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {
        "workspace.read",
        "workspace.switch",
        "members.read",
        "members.add",
        "members.remove",
    },
    "admin": {"workspace.read", "members.read", "members.add"},
    "editor": {"workspace.read"},
    "approver": {"workspace.read"},
    "viewer": {"workspace.read"},
}


def has_permission(role: str, permission: str) -> bool:
    """Return True iff role carries permission according to the map."""
    return permission in ROLE_PERMISSIONS.get(role, set())