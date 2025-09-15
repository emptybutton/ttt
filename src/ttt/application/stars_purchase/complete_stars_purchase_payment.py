from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.stars_purchase.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.stars_purchase.ports.stars_purchase_log import (
    StarsPurchaseLog,
)
from ttt.application.stars_purchase.ports.stars_purchase_views import (
    StarsPurchaseViews,
)
from ttt.application.stars_purchase.ports.stars_purchases import StarsPurchases
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.finance.payment.payment import PaymentIsNotInProcessError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CompleteStarsPurchasePayment:
    clock: Clock
    inbox: PaidStarsPurchasePaymentInbox
    users: Users
    transaction: Transaction
    map_: Map
    common_views: CommonUserViews
    stars_purchase_views: StarsPurchaseViews
    log: StarsPurchaseLog
    stars_purchases: StarsPurchases

    async def __call__(self) -> None:
        async for paid_payment in self.inbox.stream():
            current_datetime = await self.clock.current_datetime()

            async with self.transaction:
                stars_purchase = (
                    await self.stars_purchases.stars_purchase_with_id(
                        paid_payment.purchase_id,
                    )
                )

                if stars_purchase is None:
                    await self.log.no_stars_purchase_to_complete_payment(
                        paid_payment.purchase_id,
                    )
                    return

                try:
                    tracking = Tracking()
                    stars_purchase.complete_payment(
                        paid_payment.success,
                        current_datetime,
                        tracking,
                    )
                except PaymentIsNotInProcessError:
                    await self.log.double_stars_purchase_payment_completion(
                        stars_purchase,
                        paid_payment,
                    )
                else:
                    await self.log.stars_purchase_payment_completed(
                        stars_purchase,
                        paid_payment,
                    )

                    await self.map_(tracking)
                    await (
                        self.stars_purchase_views.completed_stars_purchase_view(
                            stars_purchase,
                        )
                    )
