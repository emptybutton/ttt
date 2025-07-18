from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.finance.payment.payment import PaymentIsNotInProcessError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CompleteStarsPurshasePayment:
    clock: Clock
    inbox: PaidStarsPurchasePaymentInbox
    users: Users
    transaction: Transaction
    map_: Map
    user_views: UserViews

    async def __call__(self) -> None:
        async for paid_payment in self.inbox.stream():
            current_datetime = await self.clock.current_datetime()

            async with self.transaction:
                user = await self.users.user_with_id(
                    paid_payment.location.user_id,
                )

                if user is None:
                    await (
                        self.user_views.render_user_is_not_registered_view(
                            paid_payment.location,
                        )
                    )
                    continue

                tracking = Tracking()
                try:
                    user.complete_stars_purchase_payment(
                        paid_payment.purshase_id,
                        paid_payment.success,
                        current_datetime,
                        tracking,
                    )
                except (PaymentIsNotInProcessError):
                    ...
                else:
                    await self.map_(tracking)
                    await (
                        self.user_views
                        .render_completed_stars_purshase_view(
                            user,
                            paid_payment.purshase_id,
                            paid_payment.location,
                        )
                    )
