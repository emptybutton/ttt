from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.view_player import ViewPlayer
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


view_player_router = Router(name=__name__)


@view_player_router.message(any_state, Command("profile"))
@inject
async def _(
    message: Message, view_player: FromDishka[ViewPlayer],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot), message.chat.id,
        )
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    await view_player(location)
