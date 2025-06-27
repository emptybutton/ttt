from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.view_player import ViewPlayer
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


view_player_router = Router(name=__name__)


@view_player_router.message(any_state, Command("profile"))
@inject
async def _(
    message: Message, view_player: FromDishka[ViewPlayer],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    await view_player(message.from_user.id)
