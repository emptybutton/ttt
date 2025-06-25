from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.ports.games import Games, NoGameError
from ttt.entities.core.game.game import Game
from ttt.infrastructure.sqlalchemy.tables import TableGame, TablePlayer


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresGames(Games):
    _session: AsyncSession

    async def game_with_id(self, id_: UUID | None, /) -> Game:
        table_game = await self._session.get(TableGame, id_)

        if table_game is None:
            raise NoGameError

        return table_game.entity()

    async def game_with_game_location(
        self, game_location_player_id: int, /,
    ) -> Game | None:
        join_condition = (
            (TablePlayer.id == game_location_player_id)
            & (TablePlayer.game_location_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TablePlayer, join_condition)

        table_game = await self._session.scalar(stmt)

        if table_game is None:
            return None

        return table_game.entity()
