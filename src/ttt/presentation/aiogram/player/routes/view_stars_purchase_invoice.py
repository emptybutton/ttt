from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.message import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.view_stars_purchase_invoice import (
    ViewStarsPurchaseInvoice,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.rubles import Rubles


view_stars_purchase_invoice_router = Router(name=__name__)


@view_stars_purchase_invoice_router.callback_query(
    F.data == "128_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    view_stars_purchase_invoice: FromDishka[ViewStarsPurchaseInvoice],
) -> None:
    await _route(view_stars_purchase_invoice, callback, Rubles(128, 0))


@view_stars_purchase_invoice_router.callback_query(
    F.data == "256_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    view_stars_purchase_invoice: FromDishka[ViewStarsPurchaseInvoice],
) -> None:
    await _route(view_stars_purchase_invoice, callback, Rubles(256, 0))


@view_stars_purchase_invoice_router.callback_query(
    F.data == "512_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    view_stars_purchase_invoice: FromDishka[ViewStarsPurchaseInvoice],
) -> None:
    await _route(view_stars_purchase_invoice, callback, Rubles(512, 0))


@view_stars_purchase_invoice_router.callback_query(
    F.data == "1024_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    view_stars_purchase_invoice: FromDishka[ViewStarsPurchaseInvoice],
) -> None:
    await _route(view_stars_purchase_invoice, callback, Rubles(1024, 0))


async def _route(
    view_stars_purchase_invoice: ViewStarsPurchaseInvoice,
    callback: CallbackQuery,
    rubles: Rubles,
) -> None:
    if not isinstance(callback.message, Message):
        raise TypeError

    player_id = callback.from_user.id
    chat_id = callback.message.chat.id
    location = PlayerLocation(player_id, chat_id)

    await view_stars_purchase_invoice(location, rubles)
