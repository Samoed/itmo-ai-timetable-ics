import logging
from os import environ
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy_utils import create_database, database_exists, drop_database

from itmo_ai_timetable.settings import Settings
from tests.utils import make_alembic_config


@pytest.fixture
def postgres() -> str:
    settings = Settings()

    tmp_name = f"{uuid4().hex}.pytest"
    settings.postgres_db = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_uri
    tmp_url = tmp_url.replace("postgresql+asyncpg://", "postgresql://")
    if not (database_exists(tmp_url)):
        create_database(tmp_url)

    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    logging.getLogger("alembic").setLevel(logging.CRITICAL)
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=False)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    cmd_options = SimpleNamespace(config="app/database/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine(postgres):
    """Override this fixture to provide pytest-alembic powered tests with a database handle."""
    return create_async_engine(postgres, echo=True)


@pytest.fixture
async def _migrated_postgres(postgres, alembic_config: Config):
    """Проводит миграции."""
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def engine_async(postgres, _migrated_postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine_async, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session
