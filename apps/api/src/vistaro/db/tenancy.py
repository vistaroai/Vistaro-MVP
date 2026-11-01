"""Database access and tenancy helpers.

``TEST-001`` uses this module today; repositories written later (``AUTH-002``
onward) share the same tenant-scope helper so application code and the
isolation tests cannot drift apart.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from os import getenv
from typing import Final

from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.engine import URL, make_url

#: Superuser connection used only to seed fixtures and verify DDL. Defaults to
#: the local docker-compose values; CI sets the same values for its Postgres
#: service container.
ADMIN_DATABASE_URL_ENV: Final[str] = "VISTARO_ADMIN_DATABASE_URL"
ADMIN_DATABASE_URL_DEFAULT: Final[str] = (
    "postgresql://vistaro:vistaro_local_only@localhost:5432/vistaro"
)

#: Tenant tables and their workspace column. Every new tenant table must be
#: added here so its generated isolation test exists (TEST-001 rule).
TENANT_TABLE_WORKSPACE_COLUMNS: Final[dict[str, str]] = {
    "memberships": "workspace_id",
}

#: Transaction-local so pooled connections cannot inherit another tenant's
#: scope (WARN-B-009).
SET_TENANT_SCOPE_SQL: Final = text(
    "SELECT set_config('app.workspace_id', :workspace_id, true)"
)

#: Identity scope for the current request's user. Needed for tables whose
#: rows belong to the user *and* a workspace (memberships): "my workspaces"
#: runs before any workspace is active. Also transaction-local.
SET_USER_SCOPE_SQL: Final = text(
    "SELECT set_config('app.user_id', :user_id, true)"
)


def sqlalchemy_url(raw: str) -> URL:
    """Return ``raw`` as a URL pinned to the installed psycopg 3 driver."""
    url = make_url(raw.strip())
    if url.drivername == "postgresql":
        return URL.create(
            drivername="postgresql+psycopg",
            username=url.username,
            password=url.password,
            host=url.host,
            port=url.port,
            database=url.database,
        )
    return url


def admin_database_url() -> str:
    """Return the admin connection URL (fixture and DDL use only)."""
    return getenv(ADMIN_DATABASE_URL_ENV, ADMIN_DATABASE_URL_DEFAULT)


def build_engine(raw_url: str) -> Engine:
    """Return an engine for ``raw_url`` using the psycopg 3 driver.

    libpq can hang indefinitely when the server is unreachable (for example
    during an outage or when ``/readyz`` probes down dependencies), so every
    engine bounds its connect with ``connect_timeout``.
    """
    return create_engine(
        sqlalchemy_url(raw_url),
        connect_args={"connect_timeout": 5},
    )


def set_tenant_scope(connection: Connection, workspace_id: str) -> None:
    """Scope ``connection`` to ``workspace_id`` for the current transaction.

    Uses ``set_config(..., true)`` (transaction-local); the scope ends with the
    transaction, which keeps pooled connections safe to reuse.
    """
    connection.execute(SET_TENANT_SCOPE_SQL, {"workspace_id": workspace_id})


def set_user_scope(connection: Connection, user_id: str) -> None:
    """Scope ``connection`` to ``user_id`` for the current transaction.

    Transaction-local like ``set_tenant_scope`` (WARN-B-009); used for
    user-owned tenant rows such as the caller's own memberships.
    """
    connection.execute(SET_USER_SCOPE_SQL, {"user_id": user_id})


@contextmanager
def tenant_session(
    engine: Engine,
    *,
    user_id: str,
    workspace_id: str | None = None,
) -> Iterator[Connection]:
    """Open one transaction already scoped for the caller (AUTH-002 helper).

    Sets ``app.user_id`` always and ``app.workspace_id`` when a workspace is
    known, using transaction-local GUCs only (WARN-B-009). Repositories built
    on this helper cannot forget the scope, and the scope dies with the
    transaction so pooled connections stay clean.
    Yields the scoped ``Connection``; scope resets when the block ends.
    """
    with engine.begin() as connection:
        set_user_scope(connection, user_id)
        if workspace_id is not None:
            set_tenant_scope(connection, workspace_id)
        yield connection
