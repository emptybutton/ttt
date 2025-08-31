from dataclasses import dataclass
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.get_admin_rights import GetAdminRights
from ttt.application.user.relinquish_admin_rights import RelinquishAdminRights
from ttt.application.user.view_admin_menu import ViewAdminMenu
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.hint import Hint
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class AdminMainMenuView(EncodableToWindowData):
    is_user_admin: bool


@inject
async def main_getter(
    *,
    event_from_user: User,
    view_admin_menu: FromDishka[ViewAdminMenu],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await view_admin_menu(event_from_user.id)
    view = result_buffer(AdminMainMenuView)

    return view.window_data()


@inject
async def input_admin_token(
    message: Message,
    _: MessageInput,
    manager: DialogManager,
    get_admin_rights: FromDishka[GetAdminRights],
) -> None:
    admin_token = message.text

    if admin_token is None:
        await manager.start(
            AdminDialogState.main,
            {"hint": "❌ Админ-токен должен быть в виде текста"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
        return

    await get_admin_rights(not_none(message.from_user).id, admin_token)


@inject
async def on_relinquish_admin_rights_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    relinquish_admin_rights: FromDishka[RelinquishAdminRights],
) -> None:
    await relinquish_admin_rights(callback.from_user.id)


main_window = Window(
    Const(
        "🧿 Что хотите сделать?",
        when=F["main"]["is_user_admin"] & ~F["start_data"]["hint"],
    ),
    SwitchTo(
        Const("Посмотреть профиль пользователя"),
        state=AdminDialogState.other_user_profile,
        id="other_user_profile",
        when=F["main"]["is_user_admin"],
    ),
    Button(
        Const("Отказатся от прав админа"),
        id="relinquish_admin_rights",
        on_click=on_relinquish_admin_rights_clicked,
        when=F["main"]["is_user_admin"],
    ),

    Multi(
        Const("🧿 Вы не админ"),
        Const(" "),
        Const("Что бы получить права админа введите админ-токен:"),
        when=~F["main"]["is_user_admin"] & ~F["start_data"]["hint"],
    ),
    MessageInput(
        input_admin_token,
        content_types=[ContentType.ANY],
    ),

    Hint(Format("{start_data[hint]}")),

    Start(
        Const("Вернутся в главное меню"),
        id="exit",
        state=MainDialogState.main,
        mode=StartMode.RESET_STACK,
    ),
    state=AdminDialogState.main,
    getter=main_getter,
)
