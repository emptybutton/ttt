from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.application.game.game.ports.game_log import GameLog
from ttt.entities.core.game.game import AlreadyCompletedGameError
from ttt.entities.core.user.location import UserLocation
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

    async def __call__(self, location: UserLocation) -> None:
        async with self.transaction:
            game, game_result_id = await gather(
                self.games.game_with_game_location(location.user_id),
                self.uuids.random_uuid(),
            )
            if game is None:
                await self.game_views.render_no_game_view(location)
                return

            locations = tuple(
                not_none(user.game_location)
                for user in (game.player1, game.player2)
                if isinstance(user, User)
            )

            try:
                tracking = Tracking()
                game.cancel(location.user_id, game_result_id, tracking)
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_cancel(
                    game,
                    location,
                )
                await self.game_views.render_game_already_complteted_view(
                    location,
                    game,
                )
                return

            await self.log.game_cancelled(location, game)

            await self.map_(tracking)
            await self.game_views.render_game_view_with_locations(
                locations,
                game,
            )
