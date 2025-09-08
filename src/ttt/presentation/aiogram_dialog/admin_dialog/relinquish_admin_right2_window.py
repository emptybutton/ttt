from dataclasses import dataclass
from typing import Any, Literal

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram.utils.formatting import Bold, Text
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, List, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.authorize_as_admin import AuthorizeAsAdmin
from ttt.application.user.relinquish_admin_right import RelinquishAdminRight
from ttt.application.user.view_admin_menu import ViewAdminMenu
from ttt.entities.core.user.admin_right import (
    AdminRight,
    AdminRightViaAdminToken,
    AdminRightViaOtherAdmin,
)
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@inject
async def on_yes_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    relinquish_admin_right: FromDishka[RelinquishAdminRight],
) -> None:
    await relinquish_admin_right(callback.from_user.id)


relinquish_admin_right2_window = Window(
    Const(
        Text("🧿 Вы ", Bold("абсолютно точно"), " уверены?").as_html(),
        when=~F["start"]["hint"],
    ),

    hint(key="hint"),
    Row(
        Button(
            Const("Да"),
            id="yes",
            on_click=on_yes_clicked,
        ),
        SwitchTo(
            Const("Нет"),
            id="no",
            state=AdminDialogState.main,
        ),
    ),

    OneTimekey("hint"),
    state=AdminDialogState.relinquish_admin_right2,
    parse_mode="html",
)
