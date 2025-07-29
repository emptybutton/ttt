from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.emoji_selection.wait_emoji_to_select import (
    WaitEmojiToSelect,
)
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_emoji_to_buy_select_router = Router(name=__name__)


@wait_emoji_to_buy_select_router.message(
    any_state,
    or_f(Command("select_emoji"), F.text == "Выбрать эмоджи"),
)
@inject
async def _(
    message: Message,
    wait_emoji_to_select: FromDishka[WaitEmojiToSelect],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await wait_emoji_to_select(message.from_user.id)
