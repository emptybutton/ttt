from dataclasses import dataclass

from ttt.application.user.common.ports.user_fsm import UserFsm
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitStarsToStartStarsPurshase:
    fsm: UserFsm
    user_views: UserViews
    log: StarsPurchaseUserLog

    async def __call__(self, location: UserLocation) -> None:
        await self.log.user_intends_to_buy_stars(location)
        await self.user_views.render_wait_stars_to_start_stars_purshase_view(
            location,
        )
