from aiogram import F, Router
from aiogram.types import ContentType, Message
from dishka import AsyncContainer
from dishka.integrations.aiogram import inject

from ttt.application.stars_purchase.dto.common import PaidStarsPurchasePayment
from ttt.application.stars_purchase.start_stars_purchase_payment_completion import (  # noqa: E501
    StartStarsPurchasePaymentCompletion,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.user.invoices import (
    StarsPurchaseInvoicePayload,
    invoce_payload_adapter,
)


handle_payment_router = Router(name=__name__)


@handle_payment_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
@inject
async def _(
    message: Message,
    dishka_container: AsyncContainer,
) -> None:
    aiogram_payment = not_none(message.successful_payment)
    success = PaymentSuccess(
        aiogram_payment.telegram_payment_charge_id,
        aiogram_payment.provider_payment_charge_id,
    )

    invoce_payload = invoce_payload_adapter.validate_json(
        aiogram_payment.invoice_payload,
    )

    match invoce_payload:
        case StarsPurchaseInvoicePayload():
            start_stars_purchase_payment_completion = (
                await dishka_container.get(StartStarsPurchasePaymentCompletion)
            )
            payment = PaidStarsPurchasePayment(
                invoce_payload.purchase_id,
                invoce_payload.user_id,
                success,
            )
            await start_stars_purchase_payment_completion(payment)
