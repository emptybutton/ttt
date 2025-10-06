from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery
from aiogram.types.user import User
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

from ttt.application.user.game.dont_wait_for_matchmaking import (
    DontWaitForMatchmaking,
)
from ttt.application.user.game.view_matchmaking import ViewMatchmaking
from ttt.application.user.game.wait_for_matchmaking import WaitForMatchmaking
from ttt.infrastructure.retrier import Retrier
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class GameStartView(EncodableToWindowData):
    is_user_waiting_for_matchmaking: bool


@inject
async def on_wait_for_matchmaking_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    wait_for_matchmaking: FromDishka[WaitForMatchmaking],
    retrier: FromDishka[Retrier],
) -> None:
    await retrier(wait_for_matchmaking, callback.from_user.id)


@inject
async def on_dont_wait_for_matchmaking_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    dont_wait_for_matchmaking: FromDishka[DontWaitForMatchmaking],
    retrier: FromDishka[Retrier],
) -> None:
    await retrier(dont_wait_for_matchmaking, callback.from_user.id)


@inject
async def getter(
    *,
    event_from_user: User,
    view_matchmaking: FromDishka[ViewMatchmaking],
    retrier: FromDishka[Retrier],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await retrier(view_matchmaking, event_from_user.id)
    view = result_buffer(GameStartView)

    return view.window_data()


game_start_window = Window(
    Const("⚔️ Выберите режим", when=~F["start_data"]["hint"]),
    hint(key="hint"),
    Row(
        Button(
            Const("🗡 Подбор игр"),
            id="wait_for_matchmaking",
            on_click=on_wait_for_matchmaking_clicked,
            when=~F["main"]["is_user_waiting_for_matchmaking"],
        ),
        Button(
            Const("🗡❌ Отменить"),
            id="dont_wait_for_matchmaking",
            on_click=on_dont_wait_for_matchmaking_clicked,
            when=F["main"]["is_user_waiting_for_matchmaking"],
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
    getter=getter,
)
