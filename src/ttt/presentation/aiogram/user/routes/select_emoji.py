from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


select_emoji_router = Router(name=__name__)


@select_emoji_router.message(any_state, Command("select_emoji"))
@inject
async def _(
    message: Message,
    command: CommandObject,
    select_emoji: FromDishka[SelectEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    user_id = message.from_user.id
    emoji_str = not_none(command.args)
    await select_emoji(user_id, emoji_str)
