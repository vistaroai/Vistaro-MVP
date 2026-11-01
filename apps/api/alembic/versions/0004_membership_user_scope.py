"""Memberships policy gains a user branch so members can list their own workspaces (AUTH-002).

The 0002 policy only matched ``app.workspace_id``, which blocks "list the
workspaces I belong to": that query runs before (and often without) any
workspace scope, yet owns no tenant data. The application now sets
``app.user_id`` (transaction-local, from the verified session) alongside
``app.workspace_id``; a membership row is visible when either the workspace
branch or the user branch matches.

- Cross-workspace isolation is unchanged: with no GUCs set both branches are
  NULL and deny; with another workspace's ID the branch still denies.
- WITH CHECK keeps INSERTs gated on the same two branches, so a user can only
  insert memberships the branches would let them see.
- 0002 is merged and stays immutable; this revision replaces the policy.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP POLICY tenant_isolation ON memberships")
    op.execute(
        """
        CREATE POLICY tenant_isolation ON memberships
            USING (
                workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
                OR user_id = NULLIF(current_setting('app.user_id', true), '')::uuid
            )
            WITH CHECK (
                workspace_id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
                OR user_id = NULLIF(current_setting('app.user_id', true), '')::uuid
            )
        """
    )


def downgrade() -> None:
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
