from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.select_emoji import SelectEmoji
from ttt.entities.core.player.location import PlayerLocation
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message
from ttt.presentation.aiogram.player.fsm import AiogramPlayerFsmState
from ttt.presentation.aiogram.player.parsing import parsed_emoji_str


select_emoji_router = Router(name=__name__)


@select_emoji_router.message(
    StateFilter(AiogramPlayerFsmState.waiting_emoji_to_select),
)
@inject
async def _(
    message: Message,
    select_emoji: FromDishka[SelectEmoji],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    location = PlayerLocation(message.from_user.id, message.chat.id)
    emoji_str = parsed_emoji_str(message)
    await select_emoji(location, emoji_str)
