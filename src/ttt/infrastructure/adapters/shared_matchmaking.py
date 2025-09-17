from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.matchmaking.common.shared_matchmaking import (
    SharedMatchmaking,
)
from ttt.entities.core.matchmaking.matchmaking import (
    Matchmaking,
)
from ttt.infrastructure.sqlalchemy.tables.matchmaking import (
    TableUserWaiting,
)


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresSharedMatchmaking(SharedMatchmaking):
    _session: AsyncSession

    def __await__(self) -> Generator[Any, Any, Matchmaking]:
        return self._matchmaking().__await__()

    async def _matchmaking(self) -> Matchmaking:
        stmt = select(TableUserWaiting).with_for_update()
        result = await self._session.scalars(stmt)
        table_waitings = result.all()

        return Matchmaking([it.entity() for it in table_waitings])
