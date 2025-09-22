from pydantic.dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.user.common.ports.user_locks import UserLocks
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


@dataclass(frozen=True)
class InPostgresUserLocks(UserLocks):
    _session: AsyncSession

    async def lock_user_by_id(
        self,
        user_id: int,
        /,
    ) -> None:
        stmt = select(1).select_from(TableUser).where(TableUser.id == user_id)
        await self._session.execute(stmt)
