"""Cross-workspace isolation tests for every tenant table (TEST-001).

These tests connect as the application role and prove that Row Level Security
keeps workspaces isolated even when application filters are removed. They need
the local services running (``docker compose -f infra/docker-compose.yml
up -d``) because they exercise the real database.
"""

import pytest
import sqlalchemy.exc
from sqlalchemy import text
from sqlalchemy.engine import Engine

from vistaro.db.tenancy import (
    TENANT_TABLE_WORKSPACE_COLUMNS,
    set_tenant_scope,
)


def test_unscoped_app_role_sees_no_rows(app_engine: Engine) -> None:
    """Without a workspace scope the app role must see zero tenant rows."""
    with app_engine.connect() as connection:
        count = connection.execute(
            text("SELECT count(*) FROM memberships")
        ).scalar_one()
    assert count == 0


def test_scoped_role_sees_only_its_workspace(
    app_engine: Engine, two_workspaces
) -> None:
    """Scoped to workspace A, the app role sees only A's membership."""
    with app_engine.connect() as connection:
        set_tenant_scope(connection, two_workspaces.workspace_a)
        workspace_ids = connection.execute(
            text("SELECT workspace_id FROM memberships")
        ).scalars().all()
    assert [str(value) for value in workspace_ids] == [two_workspaces.workspace_a]


def test_cross_tenant_read_with_filter_is_empty(
    app_engine: Engine, two_workspaces
) -> None:
    """A scoped query with the other workspace's ID explicitly returns zero."""
    with app_engine.connect() as connection:
        set_tenant_scope(connection, two_workspaces.workspace_a)
        count = connection.execute(
            text("SELECT count(*) FROM memberships WHERE workspace_id = :wid"),
            {"wid": two_workspaces.workspace_b},
        ).scalar_one()
    assert count == 0


def test_cross_tenant_write_is_rejected(
    app_engine: Engine, two_workspaces
) -> None:
    """Writing a row for workspace B while scoped to A violates the policy."""
    with app_engine.connect() as connection:
        set_tenant_scope(connection, two_workspaces.workspace_a)
        with pytest.raises(sqlalchemy.exc.DBAPIError, match="row-level security"):
            connection.execute(
                text(
                    "INSERT INTO memberships (workspace_id, user_id, role)"
                    " VALUES (:workspace_b, :user_a, 'viewer')"
                ),
                {
                    "workspace_b": two_workspaces.workspace_b,
                    "user_a": two_workspaces.user_a,
                },
            )


def test_pooled_connection_reuse_does_not_leak_scope(
    app_engine: Engine, two_workspaces
) -> None:
    """A committed transaction-local scope must not survive on the pooled
    connection (WARN-B-009)."""
    with app_engine.connect() as connection:
        set_tenant_scope(connection, two_workspaces.workspace_a)
        scoped = connection.execute(
            text("SELECT count(*) FROM memberships")
        ).scalar_one()

        # Return the transaction and stay on the same pooled connection.
        connection.commit()

        leaked_scope = connection.execute(
            text("SELECT current_setting('app.workspace_id', true)")
        ).scalar_one()
        unscoped = connection.execute(
            text("SELECT count(*) FROM memberships")
        ).scalar_one()

    assert scoped == 1
    assert leaked_scope in (None, "")  # no scope survives the commit
    assert unscoped == 0  # the reused connection cannot read tenant rows


@pytest.mark.parametrize(
    ("table", "workspace_column"),
    sorted(TENANT_TABLE_WORKSPACE_COLUMNS.items()),
)
def test_generated_tenant_table_isolation(
    app_engine: Engine,
    two_workspaces,
    table: str,
    workspace_column: str,
) -> None:
    """Generated per tenant table: scoped reads see own rows only.

    Every new tenant table must be registered in
    ``TENANT_TABLE_WORKSPACE_COLUMNS`` so this test covers it (TEST-001 rule).
    """
    with app_engine.connect() as connection:
        set_tenant_scope(connection, two_workspaces.workspace_a)
        total = connection.execute(
            text(f"SELECT count(*) FROM {table}")
        ).scalar_one()
        cross = connection.execute(
            text(
                f"SELECT count(*) FROM {table} WHERE {workspace_column} = :wid"
            ),
            {"wid": two_workspaces.workspace_b},
        ).scalar_one()
    assert total == 1
    assert cross == 0
