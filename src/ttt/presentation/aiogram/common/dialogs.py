from asyncio import Future
from typing import Any

from dishka.integrations.aiogram_dialog import inject
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, ListGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, Multi
from magic_filter import F


class CommonState(StatesGroup):
    main = State()
    emojis = State()
    game_mode_to_start_game = State()
    ai_type_to_start_game = State()


async def main_getter(**_: Any) -> dict[str, Any]:
    return {"is_user_in_game": False, "has_user_emojis": True}


main_window = Window(
    Const("🧭 Меню"),
    Button(
        Const("Начать игру"),
        id="start_game",
        when=~F["is_user_in_game"],
    ),
    Button(
        Const("Продолжить игру"),
        id="back_to_game",
        when=F["is_user_in_game"],
    ),
    Button(
        Const("Отменить игру"),
        id="cancel_game",
        when=F["is_user_in_game"],
    ),
    Button(Const("Профиль"), id="profile"),
    SwitchTo(
        Const("Эмоджи"),
        id="emojis",
        state=CommonState.emojis,
        when="has_user_emojis",
    ),
    Button(Const("Магазин"), id="shop"),
    state=CommonState.main,
    getter=main_getter,
)


start_game_window = Window(
    Const("⚔️ Выберите режим игры"),
    Button(Const("👥 Против человека"), id="game_against_user"),
    Button(Const("🤖 Против ИИ"), id="game_against_ai"),
    SwitchTo(Const("Назад"), id="back", state=CommonState.main),
    state=CommonState.game_mode_to_start_game,
)


async def emoji_getter(**_: Any) -> dict[str, Any]:
    return {
        "emojis": [
            {"id": "🐢", "view": "🐢"},
            {"id": "🍉", "view": "<🍉>"},
            {"id": "🐞", "view": "🐞"},
        ],
    }


@inject
async def on_emoji_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    emoji: str,
):
    print("Emoji selected:", item_id)


emoji_window = Window(
    Const("🎭 Эмоджи"),
    Select(
        Format("{item[view]}"),
        id="emojis",
        item_id_getter=lambda it: it["id"],
        items="emojis",
        on_click=on_emoji_selected,
    ),
    SwitchTo(Const("Назад"), id="back", state=CommonState.main),
    state=CommonState.emojis,
    getter=emoji_getter,
)

dialog = Dialog(
    main_window,
    emoji_window,
)
