from asyncio import Future
import random
from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import Button, ListGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.remove_emoji import RemoveEmoji


class DialogState(StatesGroup):
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
        state=DialogState.emojis,
        when="has_user_emojis",
    ),
    Button(Const("Магазин"), id="shop"),
    state=DialogState.main,
    getter=main_getter,
)


start_game_window = Window(
    Const("⚔️ Выберите режим игры"),
    Button(Const("👥 Против человека"), id="game_against_user"),
    Button(Const("🤖 Против ИИ"), id="game_against_ai"),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.game_mode_to_start_game,
)


async def emoji_getter(**_: Any) -> dict[str, Any]:
    emojis = [
        {"id": "🐢", "view": "🐢"},
        {"id": "🍉", "view": "<🍉>"},
        {"id": "🐞", "view": "🐞"},
    ]
    random.shuffle(emojis)

    return {
        "emojis": emojis,
    }


@inject
async def on_emoji_selected(
    callback: CallbackQuery,
    widget: Widget,
    dialog_manager: DialogManager,
    emoji_str: str,
    select_emoji: FromDishka[SelectEmoji],
) -> None:
    await select_emoji(callback.from_user.id, emoji_str)


@inject
async def on_selected_emoji_removed(
    callback: CallbackQuery,
    remove_emoji: FromDishka[RemoveEmoji],
) -> None:
    await remove_emoji(callback.from_user.id)


emoji_window = Window(
    Const("🎭 Эмоджи"),
    Select(
        Format("{item[view]}"),
        id="emojis",
        item_id_getter=lambda it: it["id"],
        items="emojis",
        on_click=on_emoji_selected,
    ),
    Button(
        Const("Убрать"),
        id="remove_selected_emoji",
        on_click=on_selected_emoji_removed,
    ),
    SwitchTo(Const("Назад"), id="back", state=DialogState.main),
    state=DialogState.emojis,
    getter=emoji_getter,
)

dialog = Dialog(
    main_window,
    emoji_window,
)
