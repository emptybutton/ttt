from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.remove_emoji import RemoveEmoji
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


remove_emoji_router = Router(name=__name__)


@remove_emoji_router.message(
    any_state, or_f(Command("remove_emoji"), F.text == "Убрать эмоджи"),
)
@inject
async def _(
    message: Message,
    remove_emoji: FromDishka[RemoveEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await remove_emoji(message.from_user.id)
