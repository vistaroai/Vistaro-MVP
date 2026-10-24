"""Tolerate an unset workspace scope in the memberships policy (TEST-001).

TEST-001's pooled-connection reuse test (WARN-B-009) found that after a
transaction commits, the custom GUC ``app.workspace_id`` stays present on the
pooled connection with an empty string value, and
``current_setting('app.workspace_id', true)`` then returns ``''``. Casting
``''`` to a UUID raised ``InvalidTextRepresentation`` instead of denying the
query, which would break unscoped queries on reused connections (for example
session lookups that run before a workspace is known).

``NULLIF(..., '')`` maps both ``''`` and ``NULL`` to ``NULL``, so an unscoped
query quietly sees zero rows. 0001 is already merged and stays immutable; this
revision replaces the policy.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP POLICY tenant_isolation ON memberships")
    op.execute(
        """
        CREATE POLICY tenant_isolation ON memberships
            USING (
                workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
            )
            WITH CHECK (
                workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
            )
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY tenant_isolation ON memberships")
    op.execute(
        """
        CREATE POLICY tenant_isolation ON memberships
            USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
            WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid)
        """
    )
