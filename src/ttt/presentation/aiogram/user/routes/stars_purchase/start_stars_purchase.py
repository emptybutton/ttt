from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types.message import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.stars_purchase.start_stars_purchase import (
    StartStarsPurchase,
)
from ttt.entities.core.stars import Stars


start_stars_purchase_router = Router(name=__name__)


@start_stars_purchase_router.callback_query(
    F.data == "8192_stars_purchase",
)
@inject
async def _(
    callback: CallbackQuery,
    start_stars_purchase: FromDishka[StartStarsPurchase],
) -> None:
    await _route(start_stars_purchase, callback, 8192)


@start_stars_purchase_router.callback_query(
    F.data == "16384_stars_purchase",
)
@inject
async def _(
    callback: CallbackQuery,
    start_stars_purchase: FromDishka[StartStarsPurchase],
) -> None:
    await _route(start_stars_purchase, callback, 16384)


@start_stars_purchase_router.callback_query(
    F.data == "32768_stars_purchase",
)
@inject
async def _(
    callback: CallbackQuery,
    start_stars_purchase: FromDishka[StartStarsPurchase],
) -> None:
    await _route(start_stars_purchase, callback, 32768)


@start_stars_purchase_router.callback_query(
    F.data == "65536_stars_purchase",
)
@inject
async def _(
    callback: CallbackQuery,
    start_stars_purchase: FromDishka[StartStarsPurchase],
) -> None:
    await _route(start_stars_purchase, callback, 65536)


async def _route(
    start_stars_purchase: StartStarsPurchase,
    callback: CallbackQuery,
    stars: Stars,
) -> None:
    if not isinstance(callback.message, Message):
        raise TypeError

    user_id = callback.from_user.id
    await start_stars_purchase(user_id, stars)
    await callback.answer()
