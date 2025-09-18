from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.game.ports.user_log import GameUserLog
from ttt.application.user.game.ports.user_views import GameUserViews
from ttt.entities.core.user.user import UserIsNotWaitingForMatchmakingError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class DontWaitForMatchmaking:
    map_: Map
    transaction: Transaction
    users: Users
    user_views: CommonUserViews
    views: GameUserViews
    log: GameUserLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.user_views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                user.dont_wait_for_matchmaking(tracking)
            except UserIsNotWaitingForMatchmakingError:
                await self.log.user_is_not_waiting_for_matchmaking_to_dont_wait(
                    user,
                )
                await (
                    self.views
                    .user_is_not_waiting_for_matchmaking_to_dont_wait_view(user)
                )
            else:
                await self.log.user_is_not_waiting_for_matchmaking(user)
                await self.map_(tracking)

                await self.views.user_is_not_waiting_for_matchmaking_view(user)
