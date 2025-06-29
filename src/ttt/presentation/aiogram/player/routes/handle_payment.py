from typing import cast

from aiogram import Router
from aiogram.types import ContentType, Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.ports.stars_purchase_payment_gateway import (
    PaidStarsPurchasePayment,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.nats.paid_stars_purchase_payment_inbox import (
    InNatsPaidStarsPurchasePaymentInbox,
)
from ttt.presentation.aiogram.player.invoices import (
    InvocePayload,
    StarsPurshaseInvoicePayload,
    invoce_payload_adapter,
)


handle_payment_router = Router(name=__name__)


@handle_payment_router.message(content_types=ContentType.SUCCESSFUL_PAYMENT)
@inject
async def _(
    message: Message,
    paid_stars_purchase_payment_inbox: FromDishka[
        InNatsPaidStarsPurchasePaymentInbox,
    ],
) -> None:
    payment = not_none(message.successful_payment)
    success = PaymentSuccess(
        payment.telegram_payment_charge_id,
        payment.provider_payment_charge_id,
    )

    invoce_payload = invoce_payload_adapter.validate_json(
        payment.invoice_payload,
    )

    match invoce_payload:
        case StarsPurshaseInvoicePayload():
            await paid_stars_purchase_payment_inbox.push(
                PaidStarsPurchasePayment(
                    invoce_payload.purshase_id,
                    PlayerLocation(
                        invoce_payload.location_player_id,
                        invoce_payload.location_chat_id,
                    ),
                    success,
                ),
            )
