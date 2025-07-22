from dataclasses import dataclass

from ttt.application.user.common.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.user.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.application.user.stars_purchase.ports.user_views import (
    StarsPurchaseUserViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurshasePaymentCompletion:
    inbox: PaidStarsPurchasePaymentInbox
    payment_gateway: StarsPurchasePaymentGateway
    views: StarsPurchaseUserViews
    log: StarsPurchaseUserLog

    async def __call__(self) -> None:
        async for paid_payment in self.payment_gateway.paid_payment_stream():
            await self.inbox.push(paid_payment)
            await self.views.render_stars_purchase_will_be_completed_view(
                paid_payment.location,
            )
            await self.log.stars_purshase_payment_completion_started(
                paid_payment,
            )
