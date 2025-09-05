from dataclasses import dataclass
from typing import Any, Literal

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, List, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.authorize_as_admin import AuthorizeAsAdmin
from ttt.application.user.relinquish_admin_rights import RelinquishAdminRights
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


type AdminRightName = Literal["via_admin_token", "via_other_admin"]


@dataclass(frozen=True)
class AdminMainMenuView(EncodableToWindowData):
    user_admin_right_name: AdminRightName | None
    user_admin_right: AdminRight | None
    authorized_admins_by_user: list[int]
    admins_authorized_via_admin_token_count: int
    admins_authorized_via_other_admins_count: int
    admin_count: int

    @classmethod
    def of(
        cls,
        user_admin_right: AdminRight | None,
        authorized_admins_by_user: list[int],
        admins_authorized_via_admin_token_count: int,
        admins_authorized_via_other_admins_count: int,
    ) -> "AdminMainMenuView":
        admin_count = (
            admins_authorized_via_admin_token_count
            + admins_authorized_via_other_admins_count
        )
        match user_admin_right:
            case AdminRightViaAdminToken():
                admin_right_name = "via_admin_token"
            case AdminRightViaOtherAdmin():
                admin_right_name = "via_other_admin"
            case None:
                admin_right_name = None

        return AdminMainMenuView(
            admin_right_name,
            user_admin_right,
            authorized_admins_by_user,
            admins_authorized_via_admin_token_count,
            admins_authorized_via_other_admins_count,
            admin_count=admin_count,
        )


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
    authorize_as_admin: FromDishka[AuthorizeAsAdmin],
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

    await authorize_as_admin(not_none(message.from_user).id, admin_token)


@inject
async def on_relinquish_admin_rights_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    relinquish_admin_rights: FromDishka[RelinquishAdminRights],
) -> None:
    await relinquish_admin_rights(callback.from_user.id)


is_admin_f = F["main"]["user_admin_right"].is_not(None)

main_window = Window(
    Multi(
        Format(
            "Всего админов {main[admin_count]}"
            " ({main[admins_authorized_via_admin_token_count]}"
            "+{main[admins_authorized_via_other_admins_count]})",
        ),
        Case(selector="user_admin_right_name", texts={
            "via_admin_token": Const("Вы авторизованы админ-токеном"),
            "via_other_admin": Format(
                "Вы авторизованы админом {main[user_admin_right][admin_id]}",
            ),
        }),
        Multi(
            Const("Админы, которых вы авторизовали:"),
            List(Format(" - {item}"), F["main"]["authorized_admins_by_user"]),
            when=F["main"]["authorized_admins_by_user"].len() > 0,
        ),
        Const(" "),
        Const("🧿 Что хотите сделать?"),
        when=is_admin_f & ~F["start_data"]["hint"],
    ),
    SwitchTo(
        Const("Посмотреть профиль пользователя"),
        state=AdminDialogState.other_user_profile,
        id="other_user_profile",
        when=is_admin_f,
    ),
    SwitchTo(
        Const("Выдать права админа"),
        id="authorize_other_user_as_admin",
        state=AdminDialogState.authorize_other_user_as_admin,
        when=is_admin_f,
    ),
    Button(
        Const("Отказатся от прав админа"),
        id="relinquish_admin_rights",
        on_click=on_relinquish_admin_rights_clicked,
        when=is_admin_f,
    ),

    Multi(
        Const("🧿 Вы не админ"),
        Const(" "),
        Const("Что бы получить права админа введите админ-токен:"),
        when=~is_admin_f & ~F["start_data"]["hint"],
    ),
    MessageInput(
        input_admin_token,
        content_types=[ContentType.ANY],
    ),


    hint(key="hint"),

    Start(
        Const("Вернутся в главное меню"),
        id="exit",
        state=MainDialogState.main,
        mode=StartMode.RESET_STACK,
    ),

    OneTimekey("hint"),
    state=AdminDialogState.main,
    getter=main_getter,
)
