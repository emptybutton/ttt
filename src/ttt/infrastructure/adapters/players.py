from asyncio import gather
from dataclasses import dataclass

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.common.ports.players import NoPlayerError, Players
from ttt.entities.core.player import Player
from ttt.infrastructure.loading import Loading
from ttt.infrastructure.sqlalchemy.tables import PlayerTableModel


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresPlayers(Players):
    _loading: Loading
    _session: AsyncSession

    async def assert_contains_player_with_id(self, id_: int, /) -> None:
        stmt = select(exists(1).where(PlayerTableModel.id == id_))
        contains = bool(await self._session.execute(stmt))

        if not contains:
            raise NoPlayerError(id_)

    async def player_with_id(self, id_: int, /) -> Player:
        table_player = await self._session.get(PlayerTableModel, id_)

        if table_player is None:
            raise NoPlayerError(id_)

        return self._loading.load(table_player)

    async def players_with_id(
        self, id1: int, id2: int, /,
    ) -> tuple[Player, Player]:
        return await gather(
            self.player_with_id(id1),
            self.player_with_id(id2),
        )
