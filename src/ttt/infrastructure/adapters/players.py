from collections.abc import Sequence
from dataclasses import dataclass
from typing import overload

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.player.common.ports.players import Players
from ttt.entities.core.player.player import Player
from ttt.infrastructure.sqlalchemy.tables import TablePlayer


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresPlayers(Players):
    _session: AsyncSession

    async def contains_player_with_id(
        self, id_: int, /,
    ) -> bool:
        stmt = select(exists(1).where(TablePlayer.id == id_))

        return bool(await self._session.execute(stmt))

    @overload
    async def players_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[Player | None, ...]: ...

    @overload
    async def players_with_ids(  # type: ignore[overload-cannot-match]
        self, ids: tuple[int, int], /,
    ) -> tuple[Player | None, Player | None]: ...

    async def players_with_ids(
        self, ids: Sequence[int],
    ) -> tuple[Player | None, ...]:
        players = list()

        for id_ in ids:
            player = await self.player_with_id(id_)
            players.append(player)

        return tuple(players)

    async def player_with_id(self, id_: int, /) -> Player | None:
        table_player = await self._session.get(TablePlayer, id_)

        return None if table_player is None else table_player.entity()
