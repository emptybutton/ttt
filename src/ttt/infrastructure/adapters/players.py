from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass
from typing import overload

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.common.ports.players import NoPlayerWithIDError, Players
from ttt.entities.core.player.player import Player
from ttt.infrastructure.sqlalchemy.tables import TablePlayer


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresPlayers(Players):
    _session: AsyncSession

    async def contains_player_with_id(
        self, id_: int, /,
    ) -> bool:
        stmt = select(exists(1) .where(TablePlayer.id == id_))

        return bool(await self._session.execute(stmt))

    @overload
    async def players_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[Player, ...]: ...

    @overload
    async def players_with_ids(  # type: ignore[overload-cannot-match]
        self, ids: tuple[int, int], /,
    ) -> tuple[Player, Player]: ...

    async def players_with_ids(
        self, ids: Sequence[int],
    ) -> tuple[Player, ...]:
        return tuple(await gather(*map(self.player_with_id, ids)))
