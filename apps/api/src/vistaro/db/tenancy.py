"""Database access and tenancy helpers.

``TEST-001`` uses this module today; repositories written later (``AUTH-002``
onward) share the same tenant-scope helper so application code and the
isolation tests cannot drift apart.
"""

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
