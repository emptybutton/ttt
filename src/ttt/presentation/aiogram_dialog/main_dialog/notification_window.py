from aiogram.enums import ParseMode
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
)
from aiogram_dialog.widgets.text import Const

from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


notification_window = Window(
    hint(key="hint"),
    Cancel(Const("OK")),
    state=MainDialogState.notification,
    parse_mode=ParseMode.HTML,
)
