
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from ttt.application.game.game.start_game_with_ai import StartGameWithAi
from ttt.entities.core.game.ai import AiType
from ttt.infrastructure.retrier import Retrier
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@inject
async def on_game_against_gemini_2_0_flash_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    start_game_with_ai: FromDishka[StartGameWithAi],
    retrier: FromDishka[Retrier],
) -> None:
    await retrier(
        start_game_with_ai, callback.from_user.id, AiType.gemini_2_0_flash,
    )


ai_type_to_start_game_window = Window(
    Const("🤖 Выберите тип ИИ"),
    Row(
        Button(
            Const("gemini 2.0 flash"),
            id="game_against_gemini_2_0_flash",
            on_click=on_game_against_gemini_2_0_flash_clicked,
        ),
    ),
    SwitchTo(
        Const("Назад"),
        id="back",
        state=MainDialogState.game_mode_to_start_game,
    ),
    state=MainDialogState.ai_type_to_start_game,
)
