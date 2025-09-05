from dataclasses import dataclass

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.authorize_other_user_as_admin import AuthorizeOtherUserAsAdmin
from ttt.application.user.view_other_user import ViewOtherUser
from ttt.entities.core.user.rank import rank_for_rating
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)


@inject
async def input_user_id(
    message: Message,
    _: MessageInput,
    manager: DialogManager,
    authorize_other_user_as_admin: FromDishka[AuthorizeOtherUserAsAdmin],
) -> None:
    try:
        other_user_id = int(message.text)  # type: ignore[arg-type]
    except ValueError:
        await manager.start(
            AdminDialogState.authorize_other_user_as_admin,
            {"hint": "❌ ID должен быть целочисленым числом:"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
    else:
        await authorize_other_user_as_admin(not_none(message.from_user).id, other_user_id)


authorize_other_user_as_admin_window = Window(
    Format("{start_data[hint]}", when=F["start_data"]["hint"]),

    Const(
        "🧿 Введите ID пользователя:",
        when=~F["start_data"]["profile"] & ~F["start_data"]["hint"],
    ),
    MessageInput(
        input_user_id,
        content_types=[ContentType.ANY],
    ),

    SwitchTo(Const("Назад"), id="back", state=AdminDialogState.main),

    OneTimekey("hint"),
    state=AdminDialogState.authorize_other_user_as_admin,
)
