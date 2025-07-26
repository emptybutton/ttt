from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.entities.core.game.game import AlreadyCompletedGameError
from ttt.entities.core.user.user import User
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CancelGame:
    map_: Map
    games: Games
    game_views: GameViews
    uuids: UUIDs
    transaction: Transaction
    log: GameLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            (
                game,
                user1_last_game_id,
                user2_last_game_id,
            ) = await gather(
                self.games.game_with_game_location(user_id),
                self.uuids.random_uuid(),
                self.uuids.random_uuid(),
            )
            if game is None:
                await self.game_views.no_game_view(user_id)
                return

            locations = tuple(
                not_none(user.game_location)
                for user in (game.player1, game.player2)
                if isinstance(user, User)
            )

            try:
                tracking = Tracking()
                game.cancel(
                    user_id,
                    user1_last_game_id,
                    user2_last_game_id,
                    tracking,
                )
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_cancel(game, user_id)
                await self.game_views.game_already_complteted_view(
                    user_id,
                    game,
                )
                return

            await self.log.game_cancelled(user_id, game)

            await self.map_(tracking)
            await self.game_views.game_view_with_locations(
                locations,
                game,
            )
