from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.emoji_purchase.buy_emoji import BuyEmoji
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


buy_emoji_router = Router(name=__name__)


@buy_emoji_router.message(any_state, Command("buy_emoji"))
@inject
async def _(
    message: Message,
    command: CommandObject,
    buy_emoji: FromDishka[BuyEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    user_id = message.from_user.id
    emoji_str = command.args
    await buy_emoji(user_id, emoji_str)
