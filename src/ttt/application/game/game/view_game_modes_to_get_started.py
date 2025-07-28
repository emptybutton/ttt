from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewGameModesToGetStarted:
    transaction: Transaction
    game_views: GameViews
    log: GameLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            await self.game_views.game_modes_to_get_started_view(user_id)
            await self.log.user_intends_to_start_game(user_id)
