from dataclasses import dataclass
from uuid import UUID

from ttt.application.stars_purchase.ports.stars_purchase_tasks import (
    StarsPurchaseTasks,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.infrastructure.remote_funcs.complete_stars_purchase_payment import (
    complete_stars_purchase_payment_remotely,
)


@dataclass
class NatsRemoteFuncStarsPurchaseTasks(StarsPurchaseTasks):
    async def complete_stars_purchase_payment(
        self,
        purchase_id: UUID,
        success: PaymentSuccess,
        /,
    ) -> None:
        await complete_stars_purchase_payment_remotely(
            purchase_id=purchase_id.hex,
            payment_success_id=success.id,
            payment_success_gateway_id=success.gateway_id,
        )
