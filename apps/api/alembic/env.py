"""Alembic migration environment.

Migrations run as the ``vistaro_migrator`` role through
``MIGRATOR_DATABASE_URL``; the application role (``vistaro_app``) never runs
migrations. Roles and extensions are created outside Alembic by
``infra/initdb/01_roles_and_extensions.sql`` because creating roles requires
privileges a migration role must not have.
"""

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import create_engine

from alembic import context
from vistaro.core.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

migrator_url = settings.migrator_database_url.strip()
if not migrator_url:
    raise RuntimeError(
        "MIGRATOR_DATABASE_URL is empty. Set it in .env (see .env.example); "
        "migrations must run as the vistaro_migrator role."
    )
config.set_main_option("sqlalchemy.url", migrator_url)

# Migrations are raw SQL; there is no declarative metadata to autogenerate from.
target_metadata = None


def run_migrations_offline() -> None:
    """Emit SQL to stdout without connecting to the database."""
    context.configure(
        url=migrator_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = create_engine(migrator_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
