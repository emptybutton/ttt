
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.game.game.wait_game import WaitGame
from ttt.presentation.aiogram_dialog.common.wigets.hint import Hint
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@inject
async def on_game_against_user_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    wait_game: FromDishka[WaitGame],
) -> None:
    await wait_game(callback.from_user.id)


game_start_window = Window(
    Const("⚔️ Выберите режим игры", when=~F["start_data"]["hint"]),
    Hint(Format("{start_data[hint]}")),
    Row(
        Button(
            Const("👥 Против человека"),
            id="game_against_user",
            on_click=on_game_against_user_clicked,
        ),
        SwitchTo(
            Const("🤖 Против ИИ"),
            id="game_against_ai",
            state=MainDialogState.ai_type_to_start_game,
        ),
    ),
    SwitchTo(Const("Назад"), id="back", state=MainDialogState.main),
    state=MainDialogState.game_mode_to_start_game,
)
