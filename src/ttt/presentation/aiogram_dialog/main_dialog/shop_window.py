
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const

from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


shop_window = Window(
    Const("🛒 Что хотите купить?"),
    Row(
        SwitchTo(
            Const("🌟 Звёзды"),
            id="stars_shop",
            state=MainDialogState.stars_shop,
        ),
        SwitchTo(
            Const("🎭 Эмоджи"),
            id="emoji_shop",
            state=MainDialogState.emoji_shop,
        ),
    ),
    SwitchTo(Const("Назад"), id="back", state=MainDialogState.main),
    state=MainDialogState.shop,
)
