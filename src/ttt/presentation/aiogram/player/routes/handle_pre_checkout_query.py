from aiogram import Router
from aiogram.types import PreCheckoutQuery
from dishka import AsyncContainer
from dishka.integrations.aiogram import inject

from ttt.application.player.approve_stars_purchase_invoce import (
    ApproveStarsPurchaseInvoce,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.rubles import Rubles
from ttt.presentation.aiogram.player.invoices import (
    StarsPurshaseInvoicePayload,
    invoce_payload_adapter,
)


handle_pre_checkout_query_router = Router(name=__name__)


@handle_pre_checkout_query_router.pre_checkout_query()
@inject
async def _(
    pre_checkout_query: PreCheckoutQuery,
    dishka_container: AsyncContainer,
) -> None:
    await pre_checkout_query.answer(ok=False)
    return
    payload = invoce_payload_adapter.validate_json(
        pre_checkout_query.invoice_payload,
    )

    match payload:
        case StarsPurshaseInvoicePayload():
            location = PlayerLocation(
                payload.location_player_id,
                payload.location_chat_id,
            )
            rubles = Rubles.with_total_kopecks(payload.kopecks)

            action = await dishka_container.get(ApproveStarsPurchaseInvoce)
            await action(location, rubles)
