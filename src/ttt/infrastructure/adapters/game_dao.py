from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.game_dao import GameDao
from ttt.entities.core.game.game import Game
from ttt.entities.core.user.user import User
from ttt.entities.elo.rating import GamesPlayed
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.sqlalchemy.tables.game import TableGame, TableGameState


@dataclass(frozen=True, unsafe_hash=False)
class PostgresGameDao(GameDao):
    _session: AsyncSession

    async def games_played_by_player_id(
        self,
        game: Game,
        /,
    ) -> dict[int, GamesPlayed]:
        games_played_by_player_id = dict[int, GamesPlayed]()

        if isinstance(game.player1, User):
            games_played_by_player_id[game.player1.id] = (
                await self._games_played(game.player1)
            )

        if isinstance(game.player2, User):
            games_played_by_player_id[game.player2.id] = (
                await self._games_played(game.player2)
            )

        return games_played_by_player_id

    async def _games_played(self, user: User) -> GamesPlayed:
        game_stmt = (
            select(1)
            .where(
                (TableGame.state == TableGameState.completed.value)
                & (
                    (TableGame.user1_id == user.id)
                    | (TableGame.user2_id == user.id)
                ),
            )
            .limit(31)
            .subquery()
        )
        stmt = select(func.count(1)).select_from(game_stmt)
        raw_games_played = not_none(await self._session.scalar(stmt))

        return "<=30" if raw_games_played <= 30 else ">30"  # noqa: PLR2004
