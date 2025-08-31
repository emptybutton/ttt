from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery, User
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.game.game.cancel_game import CancelGame
from ttt.application.game.game.view_game import ViewGame
from ttt.application.user.view_main_menu import ViewMainMenu
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.rank import rank_for_rating
from ttt.entities.elo.rating import EloRating
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.game_window import (
    ActiveGameView,
)
from ttt.presentation.result_buffer import ResultBuffer
from ttt.presentation.texts import rank_progres_text, rank_title


@dataclass(frozen=True)
class MainMenuView(EncodableToWindowData):
    is_user_in_game: bool
    has_user_emojis: bool
    rank_text: str
    stars: Stars

    @classmethod
    def of(
        cls,
        *,
        is_user_in_game: bool,
        has_user_emojis: bool,
        rating: EloRating,
        stars: Stars,
    ) -> "MainMenuView":
        rank = rank_for_rating(rating)

        return MainMenuView(
            is_user_in_game=is_user_in_game,
            has_user_emojis=has_user_emojis,
            rank_text=f"{rank_title(rank)} {rank_progres_text(rating)}",
            stars=stars,
        )


@inject
async def main_getter(
    *,
    event_from_user: User,
    view_main_menu: FromDishka[ViewMainMenu],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await view_main_menu(event_from_user.id)
    view = result_buffer(MainMenuView)

    return view.window_data()


@inject
async def on_cancel_game_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    cancel_game: FromDishka[CancelGame],
) -> None:
    await cancel_game(callback.from_user.id)


@inject
async def on_back_to_game_clicked(
    callback: CallbackQuery,
    _: Button,
    manager: DialogManager,
    view_game: FromDishka[ViewGame],
    result_buffer: FromDishka[ResultBuffer],
) -> None:
    await view_game(callback.from_user.id)
    view = result_buffer(ActiveGameView)
    data = view.window_data()

    await manager.start(MainDialogState.game, data, StartMode.RESET_STACK)


main_window = Window(
    Format("Вы — {main[rank_text]}"),
    Format("Звёзд: {main[stars]} 🌟"),

    Multi(
        Const(" "),
        Format("{start_data[hint]}"),
        when="start_data[hint]",
    ),

    SwitchTo(
        Const("Начать игру"),
        id="start_game",
        state=MainDialogState.game_mode_to_start_game,
        when=~F["main"]["is_user_in_game"],
    ),
    Button(
        Const("Продолжить игру"),
        id="back_to_game",
        on_click=on_back_to_game_clicked,
        when=F["main"]["is_user_in_game"],
    ),
    Button(
        Const("Отменить игру"),
        id="cancel_game",
        when=F["main"]["is_user_in_game"],
        on_click=on_cancel_game_clicked,
    ),
    SwitchTo(
        Const("Профиль"),
        id="profile",
        state=MainDialogState.profile,
    ),
    SwitchTo(
        Const("Эмоджи"),
        id="emojis",
        state=MainDialogState.emojis,
        when=F["main"]["has_user_emojis"],
    ),
    SwitchTo(
        Const("Магазин"),
        id="shop",
        state=MainDialogState.shop,
    ),

    OneTimekey("hint"),
    state=MainDialogState.main,
    getter=main_getter,
)
