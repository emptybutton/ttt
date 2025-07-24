from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.games import Games
from ttt.entities.core.game.game import Game
from ttt.infrastructure.sqlalchemy.tables import TableGame, TableUser


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresGames(Games):
    _session: AsyncSession

    async def game_with_game_location(
        self,
        game_location_user_id: int,
        /,
    ) -> Game | None:
        lock_stmt = (
            select(TableGame.id)
            .where(TableUser.game_location_game_id == TableGame.id)
            .with_for_update()
        )
        await self._session.execute(lock_stmt)

        join_condition = (
            (TableUser.id == game_location_user_id)
            & (TableUser.game_location_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TableUser, join_condition)
        table_game = await self._session.scalar(stmt)

        if table_game is None:
            return None

        return table_game.entity()
