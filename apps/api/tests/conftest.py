"""Shared fixtures for database-backed tests (TEST-001)."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

import pytest
from sqlalchemy import Engine, text

# Auth flow tests fire many POSTs through the real app's limiter; lift the
# per-peer limit for the whole test process. Threshold behavior itself is
# tested separately in test_security with a dedicated mini-app and explicit
# constructor arguments, so this override does not weaken any test.
os.environ["RATE_LIMIT_REQUESTS"] = "100000"

from vistaro.core.config import settings  # noqa: E402
from vistaro.db.tenancy import admin_database_url, build_engine  # noqa: E402

WORKSPACE_A_ID: Final[str] = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
WORKSPACE_B_ID: Final[str] = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
USER_A_ID: Final[str] = "11111111-1111-1111-1111-111111111111"
USER_B_ID: Final[str] = "22222222-2222-2222-2222-222222222222"

TRUNCATE_ALL_SQL: Final = (
    "TRUNCATE sessions, memberships, workspaces, users, email_verifications CASCADE"
)


@dataclass(frozen=True)
class TwoWorkspaces:
    """Seeded fixture data: two workspaces with one owner membership each."""

    workspace_a: str = WORKSPACE_A_ID
    workspace_b: str = WORKSPACE_B_ID
    user_a: str = USER_A_ID
    user_b: str = USER_B_ID


@pytest.fixture(name="admin_engine")
def fixture_admin_engine() -> Iterator[Engine]:
    """Superuser engine used only to seed and clean fixtures."""
    try:
        engine = build_engine(admin_database_url())
        with engine.connect() as probe:
            probe.execute(text("SELECT 1"))
    except Exception as error:  # noqa: BLE001 - surface the real reason
        pytest.skip(f"database is not reachable: {error}")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(name="app_engine")
def fixture_app_engine() -> Iterator[Engine]:
    """Engine connecting exactly as the application role (vistaro_app)."""
    engine = build_engine(settings.database_url)
    try:
        yield engine
    finally:
        engine.dispose()


def _seed_two_workspaces(engine: Engine) -> None:
    """Seed one owner membership per workspace; bypasses RLS as required."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (id, email, password_hash)"
                " VALUES (:user_a, 'owner-a@example.test', 'seed'),"
                " (:user_b, 'owner-b@example.test', 'seed')"
            ),
            {"user_a": USER_A_ID, "user_b": USER_B_ID},
        )
        connection.execute(
            text(
                "INSERT INTO workspaces (id, name, created_by)"
                " VALUES (:ws_a, 'Workspace A', :user_a),"
                " (:ws_b, 'Workspace B', :user_b)"
            ),
            {
                "ws_a": WORKSPACE_A_ID,
                "ws_b": WORKSPACE_B_ID,
                "user_a": USER_A_ID,
                "user_b": USER_B_ID,
            },
        )
        connection.execute(
            text(
                "INSERT INTO memberships (workspace_id, user_id, role)"
                " VALUES (:ws_a, :user_a, 'owner'), (:ws_b, :user_b, 'owner')"
            ),
            {
                "ws_a": WORKSPACE_A_ID,
                "ws_b": WORKSPACE_B_ID,
                "user_a": USER_A_ID,
                "user_b": USER_B_ID,
            },
        )


@pytest.fixture(name="two_workspaces")
def fixture_two_workspaces(admin_engine: Engine) -> Iterator[TwoWorkspaces]:
    """Remove any leftovers, seed two isolated workspaces, remove again after."""
    with admin_engine.begin() as connection:
        connection.execute(text(TRUNCATE_ALL_SQL))
    _seed_two_workspaces(admin_engine)
    try:
        yield TwoWorkspaces()
    finally:
        with admin_engine.begin() as connection:
            connection.execute(text(TRUNCATE_ALL_SQL))
