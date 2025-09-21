from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.game.ports.user_log import GameUserLog
from ttt.application.user.game.ports.user_views import GameUserViews
from ttt.entities.core.user.user import (
    UserAlreadyWaitingForMatchmakingError,
    UserIsInGameError,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class WaitForMatchmaking:
    map_: Map
    transaction: SerializableTransaction
    clock: Clock
    users: Users
    user_views: CommonUserViews
    views: GameUserViews
    log: GameUserLog

    async def __call__(self, user_id: int) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.transaction.commit()
                await self.user_views.user_is_not_registered_view(user_id)
                return

            current_datetime = await self.clock.current_datetime()

            try:
                tracking = Tracking()
                user.wait_for_matchmaking(current_datetime, tracking)
            except UserAlreadyWaitingForMatchmakingError:
                await self.log.user_is_already_waiting_for_matchmaking(user)
                await self.transaction.commit()
                await self.views.user_is_already_waiting_for_matchmaking_view(
                    user,
                )
            except UserIsInGameError:
                await self.log.user_is_in_game_to_wait_for_matchmaking(user)
                await self.transaction.commit()
                await self.views.user_is_in_game_to_wait_for_matchmaking_view(
                    user,
                )
            else:
                await self.log.user_is_waiting_for_matchmaking(user)
                await self.map_(tracking)
                await self.transaction.commit()
                await self.views.user_is_waiting_for_matchmaking_view(user)
