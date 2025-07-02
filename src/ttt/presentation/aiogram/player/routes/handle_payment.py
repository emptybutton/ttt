
from aiogram import F, Router
from aiogram.types import ContentType, Message
from dishka import AsyncContainer
from dishka.integrations.aiogram import inject

from ttt.application.player.common.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.buffer import Buffer
from ttt.presentation.aiogram.player.invoices import (
    StarsPurshaseInvoicePayload,
    invoce_payload_adapter,
)


handle_payment_router = Router(name=__name__)


@handle_payment_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
@inject
async def _(
    message: Message,
    dishka_container: AsyncContainer,
) -> None:
    payment = not_none(message.successful_payment)
    success = PaymentSuccess(
        payment.telegram_payment_charge_id,
        payment.provider_payment_charge_id,
    )

    invoce_payload = invoce_payload_adapter.validate_json(
        payment.invoice_payload,
    )

    parent_container = not_none(dishka_container.parent_container)
    match invoce_payload:
        case StarsPurshaseInvoicePayload():
            buffer = await parent_container.get(
                Buffer[PaidStarsPurchasePayment],
            )
            buffer.add(PaidStarsPurchasePayment(
                invoce_payload.purshase_id,
                PlayerLocation(
                    invoce_payload.location_player_id,
                    invoce_payload.location_chat_id,
                ),
                success,
            ))
