from dataclasses import dataclass

from ttt.application.stars_purchase.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.stars_purchase.ports.stars_purchase_log import (
    StarsPurchaseLog,
)
from ttt.application.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.application.stars_purchase.ports.stars_purchase_views import (
    StarsPurchaseViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchasePaymentCompletion:
    inbox: PaidStarsPurchasePaymentInbox
    payment_gateway: StarsPurchasePaymentGateway
    views: StarsPurchaseViews
    log: StarsPurchaseLog

    async def __call__(self) -> None:
        async for paid_payment in self.payment_gateway.paid_payment_stream():
            await self.inbox.push(paid_payment)
            await self.views.stars_purchase_will_be_completed_view(
                paid_payment.user_id,
            )
            await self.log.stars_purchase_payment_completion_started(
                paid_payment,
            )
