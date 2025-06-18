from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.player.ports.player_views import PlayerViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewPlayer[PlayerViewWithIDT]:
    player_views: PlayerViews[PlayerViewWithIDT]
    transaction: Transaction

    async def __call__(self, player_id: int) -> PlayerViewWithIDT:
        async with self.transaction:
            return await self.player_views.view_of_player_with_id(player_id)
