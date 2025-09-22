from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.games import Games
from ttt.entities.core.game.game import Game
from ttt.infrastructure.sqlalchemy.tables.game import TableGame
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresGames(Games):
    _session: AsyncSession

    async def current_user_game(self, user_id: int, /) -> Game | None:
        join_condition = (
            (TableUser.id == user_id)
            & (TableUser.current_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TableUser, join_condition)
        table_game = await self._session.scalar(stmt)

        if table_game is None:
            return None

        return table_game.entity()

    async def not_locked_game_with_id(self, game_id: UUID, /) -> Game | None:
        stmt = (
            select(TableGame)
            .where(TableGame.id == game_id)
            .with_for_update()
        )
        table_game = await self._session.scalar(stmt)
        return None if table_game is None else table_game.entity()
