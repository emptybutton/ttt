from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.matchmaking_queue.common.shared_matchmaking_queue import (
    SharedMatchmakingQueue,
)
from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    MatchmakingQueue,
)
from ttt.infrastructure.sqlalchemy.tables.matchmaking_queue import (
    TableUserWaiting,
)


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresSharedMatchmakingQueue(SharedMatchmakingQueue):
    _session: AsyncSession

    def __await__(self) -> Generator[Any, Any, MatchmakingQueue]:
        return self._matchmaking_queue().__await__()

    async def _matchmaking_queue(self) -> MatchmakingQueue:
        stmt = select(TableUserWaiting).with_for_update()
        result = await self._session.scalars(stmt)
        table_waitings = result.all()

        return MatchmakingQueue([it.entity() for it in table_waitings])
