from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.wait_rubles_to_view_stars_purchase_invoice import (
    WaitRublesToViewStarsPurchaseInvoice,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_rubles_to_start_stars_purshase_router = Router(name=__name__)


@wait_rubles_to_start_stars_purshase_router.message(
    any_state, Command("buy_stars"),
)
@inject
async def _(
    message: Message,
    wait_rubles_to_start_stars_purshase: FromDishka[
        WaitRublesToViewStarsPurchaseInvoice
    ],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot), message.chat.id,
        )
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    await wait_rubles_to_start_stars_purshase(location)
