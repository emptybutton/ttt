from uuid import UUID

from dishka.integrations.taskiq import FromDishka, inject

from ttt.application.stars_purchase.complete_stars_purchase_payment import (
    CompleteStarsPurchasePayment,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.infrastructure.retrier import Retrier
from ttt.infrastructure.taskiq.broker import PullSubscribe
from ttt.infrastructure.taskiq.tasks.common import nats_tasks


@nats_tasks.task(
    subject="stars_purchase.stars_purchase.complete_stars_purchase_payment",
    pull_subscribe=PullSubscribe(lambda js, subject: js.pull_subscribe(
        subject,
        "ttt-stars_purchase-stars_purchase-complete_stars_purchase_payment",
        stream="STARS_PURCHASE",
    )),
)
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
