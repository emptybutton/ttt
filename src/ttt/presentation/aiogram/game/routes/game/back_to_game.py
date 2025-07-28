from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.back_to_game import BackToGame
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


back_to_game_router = Router(name=__name__)


@back_to_game_router.message(
    any_state,
    or_f(Command("back_to_game"), (F.text == "Вернуться к игре")),
)
@inject
async def _(
    message: Message,
    back_to_game: FromDishka[BackToGame],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await back_to_game(message.from_user.id)
