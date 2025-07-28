from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews


@dataclass(frozen=True, unsafe_hash=False)
class BackToGame:
    transaction: Transaction
    game_views: GameViews
    log: GameLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            await self.game_views.current_game_view_with_user_id(user_id)
            await self.log.current_game_viewed(user_id)
