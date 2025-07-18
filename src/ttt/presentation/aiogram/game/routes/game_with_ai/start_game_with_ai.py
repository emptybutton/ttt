from aiogram import F, Router
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game_with_ai.start_game_with_ai import (
    StartGameWithAi,
)
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.user.location import UserLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


start_game_with_ai_router = Router(name=__name__)


@start_game_with_ai_router.message(
    any_state, F.data == "gemini_2_0_flash",
)
@inject
async def _(
    message: Message,
    start_game_with_ai: FromDishka[StartGameWithAi],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot), message.chat.id,
        )
        return

    await start_game_with_ai(
        UserLocation(message.from_user.id, message.chat.id),
        AiType.gemini_2_0_flash,
    )
