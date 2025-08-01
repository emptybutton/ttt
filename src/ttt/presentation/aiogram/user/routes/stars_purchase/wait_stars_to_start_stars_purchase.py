from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.stars_purchase.wait_stars_to_start_stars_purchase import (  # noqa: E501
    WaitStarsToStartStarsPurchase,
)
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_stars_to_start_stars_purchase_router = Router(name=__name__)


@wait_stars_to_start_stars_purchase_router.message(
    any_state,
    Command("buy_stars"),
)
@inject
async def _(
    message: Message,
    wait_stars_to_start_stars_purchase: FromDishka[
        WaitStarsToStartStarsPurchase
    ],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    location = message.from_user.id
    await wait_stars_to_start_stars_purchase(location)
