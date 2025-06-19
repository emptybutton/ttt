from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.ports.games import Games, NoGameError
from ttt.entities.core.game.game import Game
from ttt.infrastructure.sqlalchemy.tables import TableGame


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresGames(Games):
    _session: AsyncSession

    async def game_with_id(self, id_: UUID | None, /) -> Game:
        table_game = await self._session.get(TableGame, id_)

        if table_game is None:
            raise NoGameError(id_)

        return table_game.entity()
