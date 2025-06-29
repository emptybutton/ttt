from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.initiate_stars_purchase_payment import (
    InitiateStarsPurchasePayment,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.rubles import Rubles
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


initiate_stars_purchase_payment_router = Router(name=__name__)


@initiate_stars_purchase_payment_router.callback_query(
    F.data == "8_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    initiate_stars_purchase_payment: FromDishka[InitiateStarsPurchasePayment],
) -> None:
    await _route(initiate_stars_purchase_payment, callback, Rubles(8, 0))


@initiate_stars_purchase_payment_router.callback_query(
    F.data == "64_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    initiate_stars_purchase_payment: FromDishka[InitiateStarsPurchasePayment],
) -> None:
    await _route(initiate_stars_purchase_payment, callback, Rubles(64, 0))


@initiate_stars_purchase_payment_router.callback_query(
    F.data == "128_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    initiate_stars_purchase_payment: FromDishka[InitiateStarsPurchasePayment],
) -> None:
    await _route(initiate_stars_purchase_payment, callback, Rubles(128, 0))


@initiate_stars_purchase_payment_router.callback_query(
    F.data == "256_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    initiate_stars_purchase_payment: FromDishka[InitiateStarsPurchasePayment],
) -> None:
    await _route(initiate_stars_purchase_payment, callback, Rubles(256, 0))


@initiate_stars_purchase_payment_router.callback_query(
    F.data == "512_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    initiate_stars_purchase_payment: FromDishka[InitiateStarsPurchasePayment],
) -> None:
    await _route(initiate_stars_purchase_payment, callback, Rubles(512, 0))


@initiate_stars_purchase_payment_router.callback_query(
    F.data == "1024_rub_for_stars",
)
@inject
async def _(
    callback: CallbackQuery,
    initiate_stars_purchase_payment: FromDishka[InitiateStarsPurchasePayment],
) -> None:
    await _route(initiate_stars_purchase_payment, callback, Rubles(1024, 0))


async def _route(
    initiate_stars_purchase_payment: InitiateStarsPurchasePayment,
    callback: CallbackQuery,
    rubles: Rubles,
) -> None:
    message = callback.message

    if not isinstance(message, Message):
        raise TypeError

    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    await initiate_stars_purchase_payment(location, rubles)
