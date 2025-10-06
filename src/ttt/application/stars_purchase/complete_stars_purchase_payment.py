from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import SerializableTransaction
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
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CompleteStarsPurchasePayment:
    clock: Clock
    users: Users
    transaction: SerializableTransaction
    map_: Map
    common_views: CommonUserViews
    stars_purchase_views: StarsPurchaseViews
    log: StarsPurchaseLog
    stars_purchases: StarsPurchases

    async def __call__(
        self,
        purchase_id: UUID,
        success: PaymentSuccess,
    ) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        current_datetime = await self.clock.current_datetime()

        async with self.transaction:
            stars_purchase = (
                await self.stars_purchases.stars_purchase_with_id(
                    purchase_id,
                )
            )

            if stars_purchase is None:
                await self.log.no_stars_purchase_to_complete_payment(
                    purchase_id,
                )
                await self.transaction.commit()
                return

            try:
                tracking = Tracking()
                stars_purchase.complete_payment(
                    success,
                    current_datetime,
                    tracking,
                )
            except PaymentIsNotInProcessError:
                await self.log.double_stars_purchase_payment_completion(
                    stars_purchase,
                    success,
                )
                await self.transaction.commit()
            else:
                await self.log.stars_purchase_payment_completed(
                    stars_purchase,
                    success,
                )
                await self.map_(tracking)
                await self.transaction.commit()
                await (
                    self.stars_purchase_views.completed_stars_purchase_view(
                        stars_purchase,
                    )
                )
