from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_starting_queue import (
    GameStartingQueue,
)
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    users: Users
    game_starting_queue: GameStartingQueue
    user_views: CommonUserViews
    game_views: GameViews
    transaction: Transaction
    log: GameLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            if not await self.users.contains_user_with_id(user_id):
                await self.user_views.user_is_not_registered_view(user_id)
                return

            push = await self.game_starting_queue.push(user_id)

            if push.was_location_dedublicated:
                await self.log.double_waiting_for_game_start(user_id)
                await self.game_views.double_waiting_for_game_view(user_id)
            else:
                await self.log.waiting_for_game_start(user_id)
                await self.game_views.waiting_for_game_view(user_id)
