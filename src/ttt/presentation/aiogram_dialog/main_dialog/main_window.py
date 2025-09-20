from dataclasses import dataclass
from typing import Any, Literal

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
from ttt.application.invitation_to_game.game.view_one_incoming_invitation_to_game import (  # noqa: E501
    ViewOneIncomingInvitationToGame,
)
from ttt.application.user.view_main_menu import ViewMainMenu
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.rank import UsersWithMaxRating, rank
from ttt.entities.elo.rating import EloRating
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.func_text import FuncText
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.game_window import (
    ActiveGameView,
)
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitation_to_game_window import (  # noqa: E501
    IncomingInvitationToGameView,
)
from ttt.presentation.result_buffer import ResultBuffer
from ttt.presentation.texts import rank_progres_text, rank_title


type AmoutOfIncomingInvitationsToGame = Literal["no", "one", "many"]


@dataclass(frozen=True)
class IncomingInvitationToGameData:
    id_hex: str


@dataclass(frozen=True)
class MainMenuView(EncodableToWindowData):
    is_user_in_game: bool
    has_user_emojis: bool
    rating: EloRating
    max_rating: EloRating
    users_with_max_rating: UsersWithMaxRating
    stars: Stars
    amout_of_incoming_invitations_to_game: AmoutOfIncomingInvitationsToGame


async def rank_text(  # noqa: RUF029
    data: dict[str, Any],
    _: DialogManager,
) -> str:
    rating = data["main"]["rating"]
    max_rating = data["main"]["max_rating"]
    users_with_max_rating = data["main"]["users_with_max_rating"]
    rank_ = rank(rating, max_rating, users_with_max_rating)

    return f"Вы — {rank_title(rank_)} {rank_progres_text(rank_, rating)}"


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


@inject
async def on_incoming_invitation_to_game_clicked(
    callback_query: CallbackQuery,
    _: Button,
    manager: DialogManager,
    view_invitation_to_game: FromDishka[ViewOneIncomingInvitationToGame],
    result_buffer: FromDishka[ResultBuffer],
) -> None:
    await view_invitation_to_game(callback_query.from_user.id)
    view = result_buffer.result

    if not isinstance(view, IncomingInvitationToGameView | None):
        raise TypeError

    if view is None:
        await manager.start(
            MainDialogState.main,
            {"hint": "😭 Предложение отклонено"},
            StartMode.RESET_STACK,
        )
        return

    start_data = view.window_data()
    await manager.start(MainDialogState.incoming_invitation_to_game, start_data)


main_window = Window(
    FuncText(rank_text),
    Format("Звёзд: {main[stars]} 🌟"),
    Multi(
        Const(" "),
        Format("{start_data[hint]}"),
        when=F["start_data"]["hint"],
    ),

    Button(
        Const("Предложение к игре"),
        id="incoming_invitation_to_game",
        when=(
            ~F["main"]["is_user_in_game"]
            & (F["main"]["amout_of_incoming_invitations_to_game"] == "one")
        ),
        on_click=on_incoming_invitation_to_game_clicked,
    ),
    SwitchTo(
        Const("Предложения к игре"),
        id="incoming_invitations_to_game",
        when=F["main"]["amout_of_incoming_invitations_to_game"] == "many",
        state=MainDialogState.incoming_invitations_to_game,
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
