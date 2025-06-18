from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.ports.game_views import GameViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewGame[GameViewT]:
    game_views: GameViews[GameViewT]
    transaction: Transaction

    async def __call__(self, player_id: int) -> GameViewT:
        async with self.transaction:
            return await self.game_views.view_game_of_player_with_id(player_id)
