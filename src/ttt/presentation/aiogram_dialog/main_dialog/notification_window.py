from aiogram.enums import ContentType, ParseMode
from aiogram.types.message import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
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
