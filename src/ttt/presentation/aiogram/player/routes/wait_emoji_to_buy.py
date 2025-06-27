from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.wait_emoji_to_buy import WaitEmojiToBuy
from ttt.entities.core.player.location import PlayerLocation
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_emoji_to_buy_router = Router(name=__name__)


@wait_emoji_to_buy_router.message(any_state, Command("buy_emoji"))
@inject
async def _(
    message: Message,
    wait_emoji_to_buy: FromDishka[WaitEmojiToBuy],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    await wait_emoji_to_buy(location)
