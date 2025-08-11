from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, User
from aiogram.utils.formatting import Underline
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Multi, Text
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.game.game.back_to_game import BackToGame
from ttt.application.game.game.cancel_game import CancelGame
from ttt.application.game.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.game.start_game_with_ai import StartGameWithAi
from ttt.application.game.game.wait_game import WaitGame
from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.view_main_menu import ViewMainMenu
from ttt.application.user.view_user import ViewUser
from ttt.application.user.view_user_emojis import ViewUserEmojis
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.game.cell_number import CellNumber
from ttt.entities.core.game.game import Game, cell_emoji, is_player_move_expected
from ttt.presentation.adapters.user_views import (
    EmojiListView,
    UserMenuView,
    UserProfileView,
)
from ttt.presentation.result_buffer import ResultBuffer


class DialogState(StatesGroup):
    main = State()
    emojis = State()
    profile = State()
    game_mode_to_start_game = State()
    ai_type_to_start_game = State()
    active_game = State()
    completed_game = State()


@inject
async def main_getter(
    *,
    event_from_user: User,
    view_main_menu: FromDishka[ViewMainMenu],
    result_buffer: FromDishka[ResultBuffer],
    **_,
) -> dict[str, Any]:
    await view_main_menu(event_from_user.id)
    view = result_buffer(UserMenuView)

    return {"view": view}


@inject
async def on_back_to_game_clicked(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    ___: Any,
    back_to_game: FromDishka[BackToGame],
) -> None:
    await back_to_game(callback.from_user.id)


@inject
async def on_cancel_game_clicked(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    ___: Any,
    cancel_game: FromDishka[CancelGame],
) -> None:
    await cancel_game(callback.from_user.id)


main_window = Window(
    Case(
        selector=F["player_result_in_game"]["type"],
        texts={
            "win": Const("Вы победили!"),
            "loss": Const("Вы проиграли!"),
            "draw": Const("Ничья!"),
        },
        when="player_result_in_game",
    ),
    Const(" ", when="player_result_in_game"),
    Format(
        "{player_result_in_game[rating_vector]} 🏅",
        when="player_result_in_game",
    ),
    Format(
        "+{player_result_in_game[new_stars]} 🌟", when="player_result_in_game",
    ),

    Const("🧭 Меню", when="is_header_empty"),

    SwitchTo(
        Const("Начать игру"),
        id="start_game",
        state=DialogState.game_mode_to_start_game,
        when=~F["view"].is_user_in_game,
    ),
    Button(
        Const("Продолжить игру"),
        id="back_to_game",
        when=F["view"].is_user_in_game,
        on_click=on_back_to_game_clicked,
    ),
    Button(
        Const("Отменить игру"),
        id="cancel_game",
        when=F["view"].is_user_in_game,
        on_click=on_cancel_game_clicked,
    ),
    SwitchTo(
        Const("Профиль"),
        id="profile",
        state=DialogState.profile,
    ),
    SwitchTo(
        Const("Эмоджи"),
        id="emojis",
        state=DialogState.emojis,
        when=F["view"].has_user_emojis,
    ),
    Button(Const("Магазин"), id="shop"),
    state=DialogState.main,
    getter=main_getter,
)


@inject
async def on_game_against_user_selected(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    ___: Any,
    wait_game: FromDishka[WaitGame],
) -> None:
    await wait_game(callback.from_user.id)


game_start_window = Window(
    Const("⚔️ Выберите режим игры"),
    Button(
        Const("👥 Против человека"),
        id="game_against_user",
        on_click=on_game_against_user_selected,
    ),
    Button(Const("🤖 Против ИИ"), id="game_against_ai"),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.game_mode_to_start_game,
)


@inject
async def on_game_against_gemini_2_0_flash_selected(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    ___: Any,
    start_game_with_ai: FromDishka[StartGameWithAi],
) -> None:
    await start_game_with_ai(callback.from_user.id, AiType.gemini_2_0_flash)


ai_type_to_start_game_window = Window(
    Const("🤖 Выберите тип ИИ"),
    Button(
        Const("gemini 2.0 flash"),
        id="game_against_gemini_2_0_flash",
        on_click=on_game_against_gemini_2_0_flash_selected,
    ),
    SwitchTo(
        Const("Назад"), id="back", state=DialogState.game_mode_to_start_game,
    ),
    state=DialogState.ai_type_to_start_game,
)


@inject
async def on_cell_clicked(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    id_: str,
    make_move_in_game: FromDishka[MakeMoveInGame],
) -> None:
    cell_number_int = int(id_[-1])
    await make_move_in_game(callback.from_user.id, cell_number_int)


def cell_button(cell_number_int: int) -> Button:
    return Button(
        Format(f"{{cell_views[{cell_number_int}]}}"),
        id=f"game_cell_{cell_number_int}",
        on_click=on_cell_clicked,
    )


def active_game_window_data(game: Game, user_id: int) -> dict[str, Any]:
    cell_views = dict[int, str]()

    for cell_number_int in range(1, 10):
        cell_number = CellNumber(cell_number_int)
        cell_emoji_ = cell_emoji(game, cell_number.board_position())

        cell_view = " " if cell_emoji_ is None else cell_emoji_.str_
        cell_views[cell_number_int] = cell_view

    return {
        "is_current_players_move_expected": (
            is_player_move_expected(user_id, game)
        ),
        "cell_views": cell_views,
        "is_user_player1": game.player1.id == user_id,
        "player1_emoji": game.player1_emoji.str_,
        "player2_emoji": game.player2_emoji.str_,
    }


active_game_window = Window(
    Case(selector="is_user_player1", texts={
        True: Format("Вы — {player1_emoji}, Враг — {player1_emoji}"),
        False: Format("Враг — {player1_emoji}, Вы — {player1_emoji}"),
    }),
    Case(selector="is_current_players_move_expected", texts={
        True: Const("Ходите"),
        False: Const("Ждите хода врага"),
    }),
    Group(
        Row(cell_button(1), cell_button(2), cell_button(3)),
        Row(cell_button(4), cell_button(5), cell_button(6)),
        Row(cell_button(7), cell_button(8), cell_button(9)),
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.active_game,
)


@inject
async def emoji_getter(
    *,
    event_from_user: User,
    view_user_emojis: FromDishka[ViewUserEmojis],
    result_buffer: FromDishka[ResultBuffer],
    **_,
) -> dict[str, Any]:
    await view_user_emojis(event_from_user.id)
    list_view = result_buffer(EmojiListView)

    return {
        "emojis": list_view.views,
        "is_any_emoji_selected": list_view.is_any_emoji_selected,
        "need_to_paginate": len(list_view.views) > 7,  # noqa: PLR2004
    }


@inject
async def on_emoji_selected(
    callback: CallbackQuery,
    _: Widget,
    __: DialogManager,
    emoji_str: str,
    select_emoji: FromDishka[SelectEmoji],
) -> None:
    await select_emoji(callback.from_user.id, emoji_str)


emoji_window = Window(
    Const("🎭 Эмоджи"),
    Select(
        Format("{item}"),
        id="not_paginated_emojis",
        item_id_getter=lambda it: it.emoji_str,
        items="emojis",
        on_click=on_emoji_selected,
        when=~F["need_to_paginate"],
    ),
    ScrollingGroup(
        Select(
            Format("{item}"),
            id="paginated_emojis_page",
            item_id_getter=lambda it: it.emoji_str,
            items="emojis",
            on_click=on_emoji_selected,
        ),
        width=4,
        height=4,
        id="paginated_emojis",
        when=F["need_to_paginate"],
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.emojis,
    getter=emoji_getter,
)


@inject
async def profile_getter(
    *,
    event_from_user: User,
    view_user: FromDishka[ViewUser],
    result_buffer: FromDishka[ResultBuffer],
    **_,
) -> dict[str, Any]:
    await view_user(event_from_user.id)
    view = result_buffer(UserProfileView)

    return {"view": view}


profile_window = Window(
    Multi(
        Const("🎭 Профиль"),
        Const(" "),
        Format("🌟 Звёзд: {view.account_stars}"),
        Format("🏅 Рейтинг: {view.rating_text}"),
        Format("🏆 Побед: {view.number_of_wins}"),
        Format("💀 Поражений: {view.number_of_defeats}"),
        Format("🕊️ Ничьих: {view.number_of_draws}"),
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.profile,
    getter=profile_getter,
)


dialog = Dialog(
    main_window,
    game_start_window,
    ai_type_to_start_game_window,
    active_game_window,
    profile_window,
    emoji_window,
)
