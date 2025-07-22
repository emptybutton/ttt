from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.emoji_purchase.buy_emoji import BuyEmoji
from ttt.entities.core.user.location import UserLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message
from ttt.presentation.aiogram.user.fsm import AiogramUserFsmState
from ttt.presentation.aiogram.user.parsing import parsed_emoji_str


buy_emoji_router = Router(name=__name__)


@buy_emoji_router.message(
    StateFilter(AiogramUserFsmState.waiting_emoji_to_buy),
)
@inject
async def _(
    message: Message,
    buy_emoji: FromDishka[BuyEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    location = UserLocation(message.from_user.id, message.chat.id)
    emoji_str = parsed_emoji_str(message)
    await buy_emoji(location, emoji_str)
