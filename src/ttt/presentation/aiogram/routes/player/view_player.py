from aiogram import Router
from aiogram.filters import Command
from aiogram.methods.send_message import SendMessage
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.view_player import ViewPlayer
from ttt.presentation.aiogram.messages.common import anons_are_rohibited_message


view_player_router = Router(name=__name__)


@view_player_router.message(Command("start"))
@inject
async def _(
    message: Message, view_player: FromDishka[ViewPlayer[SendMessage]],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    send_message = await view_player(message.from_user.id)
    await send_message
