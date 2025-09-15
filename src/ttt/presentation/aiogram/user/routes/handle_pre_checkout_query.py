from aiogram import Router
from aiogram.types import PreCheckoutQuery
from dishka import AsyncContainer
from dishka.integrations.aiogram import inject

from ttt.application.stars_purchase.start_stars_purchase_payment import (
    StartStarsPurchasePayment,
)
from ttt.presentation.aiogram.user.invoices import (
    StarsPurchaseInvoicePayload,
    invoce_payload_adapter,
)


handle_pre_checkout_query_router = Router(name=__name__)


@handle_pre_checkout_query_router.pre_checkout_query()
@inject
async def _(
    pre_checkout_query: PreCheckoutQuery,
    dishka_container: AsyncContainer,
) -> None:
    invoce_payload = invoce_payload_adapter.validate_json(
        pre_checkout_query.invoice_payload,
    )

    match invoce_payload:
        case StarsPurchaseInvoicePayload():
            action = await dishka_container.get(StartStarsPurchasePayment)
            await action(invoce_payload.purchase_id)
