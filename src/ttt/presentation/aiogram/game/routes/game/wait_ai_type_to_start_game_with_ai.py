from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.game.wait_ai_type_to_start_game_with_ai import (
    WaitAiTypeToStartGameWithAi,
)
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


wait_ai_type_to_start_game_with_ai_router = Router(name=__name__)


@wait_ai_type_to_start_game_with_ai_router.message(
    any_state,
    Command("game_with_ai"),
)
@inject
async def _(
    message: Message,
    wait_ai_type_to_start_game_with_ai: FromDishka[WaitAiTypeToStartGameWithAi],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await wait_ai_type_to_start_game_with_ai(
        message.from_user.id,
    )


@wait_ai_type_to_start_game_with_ai_router.callback_query(
    any_state,
    F.data == "game_mode_against_ai_to_wait_ai_type_to_start_game",
)
@inject
async def _(
    callback: CallbackQuery,
    wait_ai_type_to_start_game_with_ai: FromDishka[WaitAiTypeToStartGameWithAi],
) -> None:
    await wait_ai_type_to_start_game_with_ai(callback.from_user.id)
    await callback.answer()
