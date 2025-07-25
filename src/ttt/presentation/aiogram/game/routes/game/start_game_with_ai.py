from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.start_game_with_ai import (
    StartGameWithAi,
)
from ttt.entities.core.game.ai import AiType


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

    await start_game_with_ai(
        callback.from_user.id,
        AiType.gemini_2_0_flash,
    )
    await callback.answer()
