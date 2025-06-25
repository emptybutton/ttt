from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.player.ports.player_views import PlayerViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewPlayer:
    player_views: PlayerViews
    transaction: Transaction

    async def __call__(self, player_id: int) -> None:
        async with self.transaction:
            await self.player_views.render_view_of_player_with_id(player_id)
