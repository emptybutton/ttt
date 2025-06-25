from dataclasses import dataclass

from ttt.application.common.ports.map import Map, NotUniquePlayerIdError
from ttt.application.common.ports.transaction import Transaction
from ttt.application.player.ports.player_views import PlayerViews
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.player import register_player
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterPlayer:
    transaction: Transaction
    player_views: PlayerViews
    map: Map

    async def __call__(self, player_id: int, player_chat_id: int) -> None:
        location = PlayerLocation(player_id, player_chat_id)

        tracking = Tracking()
        register_player(player_id, tracking)

        async with self.transaction:
            try:
                await self.map(tracking)
            except NotUniquePlayerIdError:
                await self.player_views.render_player_already_registered_view(
                    location,
                )
            else:
                await self.player_views.render_player_registered_view(location)
