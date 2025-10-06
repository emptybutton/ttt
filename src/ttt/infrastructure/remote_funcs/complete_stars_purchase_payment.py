from uuid import UUID

from dishka import AsyncContainer

from ttt.application.stars_purchase.complete_stars_purchase_payment import (
    CompleteStarsPurchasePayment,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.infrastructure.remote_funcs.nats_remote_func import nats_remote
from ttt.infrastructure.retrier import Retrier


@nats_remote(
    subject="stars_purchase.stars_purchase.complete_stars_purchase_payment",
    pull_subscribe=lambda js, subject: js.pull_subscribe(
        subject,
        "ttt-stars_purchase-stars_purchase-complete_stars_purchase_payment",
        stream="STARS_PURCHASE",
    ),
)
async def complete_stars_purchase_payment_remotely(
    container: AsyncContainer,
    *,
    purchase_id: str,
    payment_success_id: str,
    payment_success_gateway_id: str,
) -> None:
    payment_success = PaymentSuccess(
        payment_success_id, payment_success_gateway_id,
    )

    retrier = await container.get(Retrier)
    complete_stars_purchase_payment = await container.get(
        CompleteStarsPurchasePayment,
    )
    await retrier(
        complete_stars_purchase_payment,
        UUID(hex=purchase_id),
        payment_success,
    )
