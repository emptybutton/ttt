from aiogram import F, Router
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.make_move_in_game import MakeMoveInGame
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import (
    anons_are_rohibited_message,
)


make_move_in_game_router = Router(name=__name__)


@make_move_in_game_router.message(F.text.regexp(r"^\d+$"))
@inject
async def _(
    message: Message,
    make_move_in_game: FromDishka[MakeMoveInGame],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    cell_number_int = int(not_none(message.text))

    await make_move_in_game(
        message.from_user.id,
        cell_number_int,
    )
