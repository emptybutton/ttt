from collections.abc import Sequence
from dataclasses import dataclass
from typing import overload

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.user import User
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresUsers(Users):
    _session: AsyncSession
    _users_to_matchmake_limit: int

    async def contains_user_with_id(
        self,
        id_: int,
        /,
    ) -> bool:
        stmt = select(exists(1).where(TableUser.id == id_)).with_for_update()

        return bool(await self._session.execute(stmt))

    @overload
    async def users_with_ids(
        self,
        ids: Sequence[int],
        /,
    ) -> tuple[User | None, ...]: ...

    @overload
    async def users_with_ids(  # type: ignore[overload-cannot-match]
        self,
        ids: tuple[int, int],
        /,
    ) -> tuple[User | None, User | None]: ...

    async def users_with_ids(
        self,
        ids: Sequence[int],
    ) -> tuple[User | None, ...]:
        users = list()

        for id_ in ids:
            user = await self.user_with_id(id_)
            users.append(user)

        return tuple(users)

    async def user_with_id(self, id_: int, /) -> User | None:
        stmt = select(TableUser).where(TableUser.id == id_).with_for_update()
        table_user = await self._session.scalar(stmt)

        return None if table_user is None else table_user.entity()

    async def some_users_waiting_for_matchmaking_to_matchmake(
        self,
    ) -> list[User]:
        stmt = (
            select(TableUser)
            .where(TableUser.has_matchmaking_waiting)
            .limit(self._users_to_matchmake_limit)
            .with_for_update(skip_locked=True)
        )
        result = await self._session.scalars(stmt)
        table_users = result.all()

        return [table_user.entity() for table_user in table_users]
