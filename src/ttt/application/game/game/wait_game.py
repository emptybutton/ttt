from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.waiting_locations import WaitingLocations
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.application.player.common.ports.players import Players
from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    players: Players
    waiting_locations: WaitingLocations
    player_views: PlayerViews
    game_views: GameViews
    transaction: Transaction

    async def __call__(self, location: PlayerLocation) -> None:
        async with self.transaction:
            if not await self.players.contains_player_with_id(
                location.player_id,
            ):
                await self.player_views.render_player_is_not_registered_view(
                    location,
                )
                return

            push = await self.waiting_locations.push(location)

            if push.was_location_dedublicated:
                await self.game_views.render_double_waiting_for_game_view(
                    location,
                )
            else:
                await self.game_views.render_waiting_for_game_view(location)
