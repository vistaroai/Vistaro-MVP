"""Base identity and tenancy schema (DB-001).

Creates ``users``, ``workspaces``, ``memberships`` and ``sessions`` per
``docs/ARCHITECTURE.md``. Tenancy rules (ADR-005):

- ``memberships`` is the only table in this revision that carries
  ``workspace_id``, so it is the only tenant table here. RLS is enabled,
  forced, and uses a transaction-local ``app.workspace_id`` setting so pooled
  connections cannot inherit another tenant's context (WARN-B-009).
- ``sessions`` intentionally has no workspace RLS: it is looked up before a
  workspace is known (WARN-D-007). It is scoped by ``user_id`` in application
  code and stores only the hash of the session ID.
- ``workspaces`` in later revisions may gain a policy based on membership;
  visibility is currently enforced in application code (``AUTH-002``).

Roles and extensions are created by ``infra/initdb/01_roles_and_extensions.sql``,
not by this migration. Tables end up owned by ``vistaro_migrator`` because
migrations run as that role.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            email CITEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_sub TEXT UNIQUE,
            email_verified_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE workspaces (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            created_by UUID NOT NULL REFERENCES users (id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE memberships (
            workspace_id UUID NOT NULL REFERENCES workspaces (id),
            user_id UUID NOT NULL REFERENCES users (id),
            role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'editor', 'approver', 'viewer')),
            PRIMARY KEY (workspace_id, user_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE sessions (
            id_hash TEXT PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users (id),
            active_workspace_id UUID REFERENCES workspaces (id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_seen_at TIMESTAMPTZ NOT NULL,
            expires_at TIMESTAMPTZ NOT NULL
        )
        """
    )
    op.execute("CREATE INDEX memberships_user_id_idx ON memberships (user_id)")
    op.execute("CREATE INDEX sessions_user_id_idx ON sessions (user_id)")
    op.execute(
        """
        ALTER TABLE memberships ENABLE ROW LEVEL SECURITY
        """
    )
    op.execute(
        """
        ALTER TABLE memberships FORCE ROW LEVEL SECURITY
        """
    )
    op.execute(
        """
        CREATE POLICY tenant_isolation ON memberships
            USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
            WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid)
        """
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE "
        "ON users, workspaces, memberships, sessions TO vistaro_app"
    )


def downgrade() -> None:
    op.execute("DROP TABLE sessions")
    op.execute("DROP TABLE memberships")
    op.execute("DROP TABLE workspaces")
    op.execute("DROP TABLE users")
