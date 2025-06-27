from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message, Sticker
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.buy_emoji import BuyEmoji
from ttt.entities.core.player.location import PlayerLocation
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message
from ttt.presentation.aiogram.player.fsm import AiogramPlayerFsmState


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
        await anons_are_rohibited_message(message)
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)

    match message:
        case Message(text=str() as text):
            emoji_str = text
        case Message(sticker=Sticker(emoji=str() as emoji)):
            emoji_str = emoji
        case _:
            emoji_str = None

    await buy_emoji(location, emoji_str)
