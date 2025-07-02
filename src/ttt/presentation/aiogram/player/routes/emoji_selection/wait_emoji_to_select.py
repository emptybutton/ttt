from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.emoji_selection.wait_emoji_to_select import (
    WaitEmojiToSelect,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_emoji_to_buy_select_router = Router(name=__name__)


@wait_emoji_to_buy_select_router.message(any_state, Command("select_emoji"))
@inject
async def _(
    message: Message,
    wait_emoji_to_select: FromDishka[WaitEmojiToSelect],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot), message.chat.id,
        )
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    await wait_emoji_to_select(location)
