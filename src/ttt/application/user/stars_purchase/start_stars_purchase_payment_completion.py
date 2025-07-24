from dataclasses import dataclass

from ttt.application.user.stars_purchase.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.user.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.application.user.stars_purchase.ports.user_views import (
    StarsPurchaseUserViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchasePaymentCompletion:
    inbox: PaidStarsPurchasePaymentInbox
    payment_gateway: StarsPurchasePaymentGateway
    views: StarsPurchaseUserViews
    log: StarsPurchaseUserLog

    async def __call__(self) -> None:
        async for paid_payment in self.payment_gateway.paid_payment_stream():
            await self.inbox.push(paid_payment)
            await self.views.stars_purchase_will_be_completed_view(
                paid_payment.location,
            )
            await self.log.stars_purchase_payment_completion_started(
                paid_payment,
            )
