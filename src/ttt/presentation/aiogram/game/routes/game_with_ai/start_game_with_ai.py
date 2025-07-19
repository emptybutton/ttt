from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game_with_ai.start_game_with_ai import (
    StartGameWithAi,
)
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.user.location import UserLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


start_game_with_ai_router = Router(name=__name__)


@start_game_with_ai_router.callback_query(
    F.data == "start_game_with_gemini_2_0_flash",
)
@inject
async def _(
    callback: CallbackQuery,
    start_game_with_ai: FromDishka[StartGameWithAi],
) -> None:
    if not isinstance(callback.message, Message):
        raise TypeError

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    await start_game_with_ai(
        UserLocation(user_id, chat_id),
        AiType.gemini_2_0_flash,
    )
    await callback.answer()
