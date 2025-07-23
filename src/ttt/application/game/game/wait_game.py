from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.waiting_locations import WaitingLocations
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    users: Users
    waiting_locations: WaitingLocations
    user_views: CommonUserViews
    game_views: GameViews
    transaction: Transaction
    log: GameLog

    async def __call__(self, location: UserLocation) -> None:
        async with self.transaction:
            if not await self.users.contains_user_with_id(
                location.user_id,
            ):
                await self.user_views.user_is_not_registered_view(
                    location,
                )
                return

            push = await self.waiting_locations.push(location)

            if push.was_location_dedublicated:
                await self.log.double_waiting_for_game_start(location)
                await self.game_views.double_waiting_for_game_view(
                    location,
                )
            else:
                await self.log.waiting_for_game_start(location)
                await self.game_views.waiting_for_game_view(location)
