from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from magic_filter import F

from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)


async def input_user_id(
    message: Message,
    _: MessageInput,
    manager: DialogManager,
) -> None:
    try:
        other_user_id = int(message.text)  # type: ignore[arg-type]
    except ValueError:
        await manager.start(
            AdminDialogState.change_other_user_account2,
            {"hint": "❌ ID должен быть целочисленым числом:"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
    else:
        await manager.start(
            AdminDialogState.change_other_user_account2,
            {"other_user_id": other_user_id},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )


change_other_user_account1_window = Window(
    Multi(
        Format("{start_data[hint]}"),
        Const(" "),
        when=F["start_data"]["hint"],
    ),

    Const("🧿 Введите ID пользователя:"),
    MessageInput(
        input_user_id,
        content_types=[ContentType.ANY],
    ),

    SwitchTo(Const("Назад"), id="back", state=AdminDialogState.main),

    OneTimekey("hint"),
    state=AdminDialogState.change_other_user_account1,
)
