from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery, User
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import (
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.view_user_emojis import ViewUserEmojis
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class EmojiView:
    emoji_str: str
    emoji_str_with_selectoion: str

    @classmethod
    def of(cls, emoji_str: str, is_emoji_selected: bool) -> "EmojiView":  # noqa: FBT001
        return EmojiView(
            emoji_str=emoji_str,
            emoji_str_with_selectoion=(
                f"<{emoji_str}>" if is_emoji_selected else emoji_str
            ),
        )


@dataclass(frozen=True)
class EmojiMenuView(EncodableToWindowData):
    emoji_views: tuple[EmojiView, ...]
    is_any_emoji_selected: bool
    need_to_paginate: bool

    @classmethod
    def of(
        cls, emojis: Iterable[str], selected_emoji: str | None,
    ) -> "EmojiMenuView":
        emoji_views = tuple(
            EmojiView.of(emoji, is_emoji_selected=emoji == selected_emoji)
            for emoji in emojis
        )

        return EmojiMenuView(
            emoji_views,
            is_any_emoji_selected=selected_emoji is not None,
            need_to_paginate=len(emoji_views) > 7,  # noqa: PLR2004
        )


@inject
async def emoji_getter(
    *,
    event_from_user: User,
    view_user_emojis: FromDishka[ViewUserEmojis],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await view_user_emojis(event_from_user.id)
    view = result_buffer(EmojiMenuView)

    return view.window_data()


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
        Format("{item[emoji_str_with_selectoion]}"),
        id="not_paginated_emojis",
        item_id_getter=lambda it: it["emoji_str"],
        items=F["main"]["emoji_views"],
        on_click=on_emoji_selected,
        when=~F["main"]["need_to_paginate"],
    ),
    ScrollingGroup(
        Select(
            Format("{item[emoji_str_with_selectoion]}"),
            id="paginated_emojis_page",
            item_id_getter=lambda it: it["emoji_str"],
            items=F["main"]["emoji_views"],
            on_click=on_emoji_selected,
        ),
        width=4,
        height=4,
        id="paginated_emojis",
        when=F["main"]["need_to_paginate"],
    ),
    SwitchTo(Const("Назад"), id="back", state=MainDialogState.main),
    state=MainDialogState.emojis,
    getter=emoji_getter,
)
