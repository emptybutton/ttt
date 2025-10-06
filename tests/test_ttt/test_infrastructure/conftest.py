import warnings
from collections.abc import AsyncIterable

from pytest import fixture
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.sqlalchemy.tables.common import Base


@fixture(scope="session")
def engine(envs: Envs) -> AsyncEngine:
    return create_async_engine(str(envs.postgres_url), poolclass=NullPool)


@fixture(scope="session")
async def _session(
    engine: AsyncEngine,
) -> AsyncIterable[AsyncSession]:
    session = AsyncSession(
        engine,
        autoflush=False,
        expire_on_commit=False,
        autobegin=False,
    )

    async with session:
        yield session


@fixture
async def session(
    _session: AsyncSession,
) -> AsyncSession:
    async with _session.begin():
        await _clear_db(_session)
        return _session


async def _clear_db(session: AsyncSession) -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "Cannot correctly sort tables")

        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(delete(table))
