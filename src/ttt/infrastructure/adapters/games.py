from dataclasses import dataclass

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
        lock_stmt = (
            select(TableGame.id)
            .where(TableUser.current_game_id == TableGame.id)
            .with_for_update()
        )
        await self._session.execute(lock_stmt)

        join_condition = (
            (TableUser.id == user_id)
            & (TableUser.current_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TableUser, join_condition)
        table_game = await self._session.scalar(stmt)

        if table_game is None:
            return None

        return table_game.entity()
