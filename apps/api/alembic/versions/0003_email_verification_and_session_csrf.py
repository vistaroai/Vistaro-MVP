"""Email verification table and session-bound CSRF support (AUTH-001).

AUTH-001 needs:

- ``email_verifications``: one-time hashed verification tokens with expiry and
  a consumed marker, so reused or expired links fail (TASK_PLAYBOOK AUTH-001).
  No RLS, analogous to ``users`` and ``sessions``: rows are addressed by user
  and token before any workspace is known.
- ``sessions.csrf_token_hash``: AUTH-001 binds the browser CSRF token to the
  session (WARN-E-006 follow-through from SEC-001): after login the double
  submit token is validated against the hash stored on the session row.

Migrations run as ``vistaro_migrator`` (ALEMBIC, WARN-C-003 pattern); the
application role receives only row CRUD on the new table.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE sessions ADD COLUMN csrf_token_hash TEXT
        """
    )
    op.execute(
        """
        CREATE TABLE email_verifications (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users (id),
            token_hash TEXT UNIQUE NOT NULL,
            purpose TEXT NOT NULL CHECK (purpose IN ('signup')),
            expires_at TIMESTAMPTZ NOT NULL,
            consumed_at TIMESTAMPTZ
        )
        """
    )
    op.execute(
        "CREATE INDEX email_verifications_user_id_idx ON email_verifications (user_id)"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE "
        "ON email_verifications TO vistaro_app"
    )


def downgrade() -> None:
    op.execute("DROP TABLE email_verifications")
    op.execute(
        """
        ALTER TABLE sessions DROP COLUMN csrf_token_hash
        """
    )
