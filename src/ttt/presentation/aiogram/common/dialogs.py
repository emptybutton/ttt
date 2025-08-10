from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, User
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.view_user_emojis import ViewUserEmojis
from ttt.presentation.adapters.user_views import EmojiListView
from ttt.presentation.result_buffer import ResultBuffer


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

dialog = Dialog(
    main_window,
    emoji_window,
)
