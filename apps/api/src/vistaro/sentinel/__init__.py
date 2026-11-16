"""Sentinel package: permissions, approvals, and audit (AUTH-003, SEN-001).

AUTH-003 landed the permission map and the route-level permission dependency
here. SEN-001 extends this package with the approval state machine; it must
extend the existing map rather than introduce a second source of role truth
(WARN-B-001, WARN-B-006).
"""

from vistaro.sentinel.permissions import (
    APPROVALS_APPROVE,
    APPROVALS_REQUEST,
    MEMBERS_ADD,
    MEMBERS_READ,
    MEMBERS_REMOVE,
    PROTECTED_ROUTES,
    ROLE_PERMISSIONS,
    WORKSPACE_READ,
    WORKSPACE_SWITCH,
    ProtectedRoute,
    has_permission,
    may_approve,
    require,
)

__all__ = [
    "APPROVALS_APPROVE",
    "APPROVALS_REQUEST",
    "MEMBERS_ADD",
    "MEMBERS_READ",
    "MEMBERS_REMOVE",
    "PROTECTED_ROUTES",
    "ROLE_PERMISSIONS",
    "WORKSPACE_READ",
    "WORKSPACE_SWITCH",
    "ProtectedRoute",
    "has_permission",
    "may_approve",
    "require",
]
