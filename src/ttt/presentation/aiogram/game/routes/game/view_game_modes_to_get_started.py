from aiogram import F, Router
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.view_game_modes_to_get_started import (
    ViewGameModesToGetStarted,
)
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


view_game_modes_to_get_started_router = Router(name=__name__)


@view_game_modes_to_get_started_router.message(
    any_state, F.text == "Начать игру",
)
@inject
async def _(
    message: Message,
    view_game_modes_to_get_started: FromDishka[ViewGameModesToGetStarted],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await view_game_modes_to_get_started(message.from_user.id)
