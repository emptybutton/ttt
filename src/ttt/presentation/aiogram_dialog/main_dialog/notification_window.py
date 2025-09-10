from aiogram.enums import ContentType
from aiogram.types.message import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
)
from aiogram_dialog.widgets.text import Const

from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


notification_window = Window(
    hint(key="hint"),
    Back(Const("Назад"), id="back"),
    state=MainDialogState.notification,
)
