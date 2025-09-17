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
from magic_filter import F

from ttt.application.matchmaking.game.wait_game import WaitGame
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@inject
async def on_matchmaking_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    wait_game: FromDishka[WaitGame],
) -> None:
    await wait_game(callback.from_user.id)


game_start_window = Window(
    Const("⚔️ Выберите режим", when=~F["start_data"]["hint"]),
    hint(key="hint"),
    Row(
        Button(
            Const("🗡 Подбор игр"),
            id="matchmaking",
            on_click=on_matchmaking_clicked,
        ),
        SwitchTo(
            Const("🤖 Играть с ИИ"),
            id="single_game",
            state=MainDialogState.ai_type_to_start_game,
        ),
    ),
    Row(
        SwitchTo(
            Const("👤 Пригласить"),
            id="outcoming_invitations_to_game",
            state=MainDialogState.outcoming_invitations_to_game,
        ),
        SwitchTo(Const("Назад"), id="back", state=MainDialogState.main),
    ),

    OneTimekey("hint"),
    state=MainDialogState.game_mode_to_start_game,
)
