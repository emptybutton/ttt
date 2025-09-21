from dataclasses import dataclass
from uuid import UUID

from ttt.application.stars_purchase.ports.stars_purchase_log import (
    StarsPurchaseLog,
)
from ttt.application.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.application.stars_purchase.ports.stars_purchase_tasks import (
    StarsPurchaseTasks,
)
from ttt.application.stars_purchase.ports.stars_purchase_views import (
    StarsPurchaseViews,
)
from ttt.entities.finance.payment.success import PaymentSuccess


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchasePaymentCompletion:
    tasks: StarsPurchaseTasks
    payment_gateway: StarsPurchasePaymentGateway
    views: StarsPurchaseViews
    log: StarsPurchaseLog

    async def __call__(
        self,
        user_id: int,
        purchase_id: UUID,
        success: PaymentSuccess,
    ) -> None:
        await self.tasks.complete_stars_purchase_payment(purchase_id, success)
        await self.log.stars_purchase_payment_completion_started(
            purchase_id, success,
        )
        await self.views.stars_purchase_will_be_completed_view(user_id)
