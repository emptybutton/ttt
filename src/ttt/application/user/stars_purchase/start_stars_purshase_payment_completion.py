from dataclasses import dataclass

from ttt.application.user.common.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.user.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.application.user.common.ports.user_views import UserViews


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurshasePaymentCompletion:
    inbox: PaidStarsPurchasePaymentInbox
    payment_gateway: StarsPurchasePaymentGateway
    user_views: UserViews

    async def __call__(self) -> None:
        async for paid_payment in self.payment_gateway.paid_payment_stream():
            await self.inbox.push(paid_payment)
            await (
                self.user_views
                .render_stars_purchase_will_be_completed_view(
                    paid_payment.location,
                )
            )
