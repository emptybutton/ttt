from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.user.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.application.user.common.ports.user_fsm import UserFsm
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.location import UserLocation
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
    user_views: UserViews
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map
    log: StarsPurchaseUserLog

    async def __call__(self, location: UserLocation, stars: Stars) -> None:
        async with self.transaction:
            user, purchase_id = await gather(
                self.users.user_with_id(location.user_id),
                self.uuids.random_uuid(),
            )

            if user is None:
                await self.user_views.render_user_is_not_registered_view(
                    location,
                )
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                user.start_stars_purchase(
                    purchase_id,
                    location.chat_id,
                    stars,
                    tracking,
                )
            except InvalidStarsForStarsPurchaseError:
                await self.log.invalid_stars_for_stars_purchase(location, user, stars)
                await self.fsm.set(None)
                await (
                    self.user_views
                    .render_invalid_stars_for_stars_purchase_view(location)
                )
                return

            await self.log.user_started_stars_puchase(location, user)

            await self.map_(tracking)
            await self.fsm.set(None)
            await gather(*[
                self.payment_gateway.send_invoice(it, location)
                for it in tracking.new
                if isinstance(it, StarsPurchase)
            ])
