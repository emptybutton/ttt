from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.cancel_game import CancelGame
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


cancel_game_router = Router(name=__name__)


@cancel_game_router.message(
    any_state,
    or_f(Command("cancel_game"), (F.text == "Отменить игру")),
)
@inject
async def _(
    message: Message,
    cancel_game: FromDishka[CancelGame],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await cancel_game(message.from_user.id)
