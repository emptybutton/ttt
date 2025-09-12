
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Row, SwitchTo
from aiogram_dialog.widgets.text import Const

from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState


relinquish_admin_right1_window = Window(
    Const("Вы потеряете доступ к админ-панели"),
    Const(" "),
    Const("🧿 Вы уверены?"),

    Row(
        SwitchTo(
            Const("Да"),
            id="yes",
            state=AdminDialogState.relinquish_admin_right2,
        ),
        SwitchTo(
            Const("Нет"),
            id="no",
            state=AdminDialogState.main,
        ),
    ),
    state=AdminDialogState.relinquish_admin_right1,
)
