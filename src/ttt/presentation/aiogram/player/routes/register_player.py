from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.register_player import RegisterPlayer
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


register_player_router = Router(name=__name__)


@register_player_router.message(any_state, Command("start"))
@inject
async def _(
    message: Message, register_player: FromDishka[RegisterPlayer],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    await register_player(message.from_user.id, message.chat.id)
