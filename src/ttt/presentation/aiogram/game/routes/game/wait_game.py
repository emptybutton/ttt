from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.wait_game import WaitGame
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_game_router = Router(name=__name__)


@wait_game_router.message(any_state, Command("game"))
@inject
async def _(
    message: Message,
    wait_game: FromDishka[WaitGame],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await wait_game(message.from_user.id)
