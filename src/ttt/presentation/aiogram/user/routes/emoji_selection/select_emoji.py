from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message
from ttt.presentation.aiogram.user.fsm import AiogramUserFsmState
from ttt.presentation.aiogram.user.parsing import parsed_emoji_str


select_emoji_router = Router(name=__name__)


@select_emoji_router.message(
    StateFilter(AiogramUserFsmState.waiting_emoji_to_select),
)
@inject
async def _(
    message: Message,
    select_emoji: FromDishka[SelectEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    user_id = message.from_user.id
    emoji_str = parsed_emoji_str(message)
    await select_emoji(user_id, emoji_str)
