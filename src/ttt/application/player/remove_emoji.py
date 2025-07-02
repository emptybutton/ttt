from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.application.player.common.ports.players import Players
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RemoveEmoji:
    transaction: Transaction
    players: Players
    player_views: PlayerViews
    map_: Map

    async def __call__(self, location: PlayerLocation) -> None:
        async with self.transaction:
            player = await self.players.player_with_id(location.player_id)

            tracking = Tracking()
            player.remove_selected_emoji(tracking)

            await self.map_(tracking)
            await self.player_views.render_selected_emoji_removed_view(location)
