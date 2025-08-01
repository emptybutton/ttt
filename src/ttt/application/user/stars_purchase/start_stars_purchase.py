from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.user.common.ports.user_fsm import UserFsm
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.application.user.stars_purchase.ports.user_views import (
    StarsPurchaseUserViews,
)
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.stars_purchase import (
    InvalidStarsForStarsPurchaseError,
    StarsPurchase,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchase:
    fsm: UserFsm
    transaction: Transaction
    users: Users
    uuids: UUIDs
    clock: Clock
    common_views: CommonUserViews
    stars_purchase_views: StarsPurchaseUserViews
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map
    log: StarsPurchaseUserLog

    async def __call__(self, user_id: int, stars: Stars) -> None:
        async with self.transaction:
            user, purchase_id = await gather(
                self.users.user_with_id(user_id),
                self.uuids.random_uuid(),
            )

            if user is None:
                await self.common_views.user_is_not_registered_view(user_id)
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                user.start_stars_purchase(
                    purchase_id,
                    stars,
                    tracking,
                )
            except InvalidStarsForStarsPurchaseError:
                await self.log.invalid_stars_for_stars_purchase(
                    user,
                    stars,
                )
                await self.fsm.set(None)
                await (
                    self.stars_purchase_views
                    .invalid_stars_for_stars_purchase_view(user_id)
                )
                return

            await self.log.user_started_stars_puchase(user)

            await self.map_(tracking)
            await self.fsm.set(None)
            await gather(*[
                self.payment_gateway.send_invoice(it)
                for it in tracking.new
                if isinstance(it, StarsPurchase)
            ])
