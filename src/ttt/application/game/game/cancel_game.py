from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.entities.core.game.game import AlreadyCompletedGameError
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CancelGame:
    map_: Map
    games: Games
    game_views: GameViews
    uuids: UUIDs
    transaction: Transaction

    async def __call__(self, location: PlayerLocation) -> None:
        async with self.transaction:
            game, game_result_id = await gather(
                self.games.game_with_game_location(location.player_id),
                self.uuids.random_uuid(),
            )
            if game is None:
                await self.game_views.render_no_game_view(location)
                return

            locations = tuple(
                not_none(player.game_location)
                for player in (game.player1, game.player2)
            )

            try:
                tracking = Tracking()
                game.cancel(location.player_id, game_result_id, tracking)
            except AlreadyCompletedGameError:
                await self.game_views.render_game_already_complteted_view(
                    location, game,
                )
                return

            await self.map_(tracking)
            await self.game_views.render_game_view_with_locations(
                locations, game,
            )
