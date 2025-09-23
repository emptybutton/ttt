from uuid import UUID

from dishka.integrations.taskiq import FromDishka, inject

from ttt.application.stars_purchase.complete_stars_purchase_payment import (
    CompleteStarsPurchasePayment,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.infrastructure.retrier import Retrier
from ttt.infrastructure.taskiq.broker import NatsBroker


complete_stars_purchase_payment_broker = NatsBroker(
    "stars_purchase.stars_purchase.complete_stars_purchase_payment",
    lambda js, sub: js.pull_subscribe(
        sub,
        "ttt-stars_purchase-stars_purchase-complete_stars_purchase_payment",
        "STARS_PURCHASE",
    ),
)


@complete_stars_purchase_payment_broker.task()
@inject(patch_module=True)
async def complete_stars_purchase_payment_task(
    purchase_id: UUID,
    payment_success_id: str,
    payment_success_gateway_id: str,
    complete_stars_purchase_payment: FromDishka[CompleteStarsPurchasePayment],
    retrier: FromDishka[Retrier],
) -> None:
    payment_success = PaymentSuccess(
        payment_success_id, payment_success_gateway_id,
    )
    await retrier(complete_stars_purchase_payment, purchase_id, payment_success)
