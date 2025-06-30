from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.buy_emoji import BuyEmoji
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message
from ttt.presentation.aiogram.player.fsm import AiogramPlayerFsmState
from ttt.presentation.aiogram.player.parsing import parsed_emoji_str


buy_emoji_router = Router(name=__name__)


@buy_emoji_router.message(
    StateFilter(AiogramPlayerFsmState.waiting_emoji_to_buy),
)
@inject
async def _(
    message: Message,
    buy_emoji: FromDishka[BuyEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot), message.chat.id,
        )
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    emoji_str = parsed_emoji_str(message)
    await buy_emoji(location, emoji_str)
