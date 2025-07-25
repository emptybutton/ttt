from dataclasses import dataclass

from ttt.application.user.common.ports.user_fsm import UserFsm
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.application.user.stars_purchase.ports.user_views import (
    StarsPurchaseUserViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class WaitStarsToStartStarsPurchase:
    fsm: UserFsm
    views: StarsPurchaseUserViews
    log: StarsPurchaseUserLog

    async def __call__(self, user_id: int) -> None:
        await self.log.user_intends_to_buy_stars(user_id)
        await self.views.wait_stars_to_start_stars_purchase_view(user_id)
