from dataclasses import dataclass, field
from typing import Any, Literal

from aiogram.enums import ContentType, ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.authorize_as_admin import AuthorizeAsAdmin
from ttt.application.user.relinquish_admin_right import RelinquishAdminRight
from ttt.application.user.view_admin_menu import ViewAdminMenu
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.admin_dialog.common import (
    AdminDialogState,
    AdminRightName,
    admin_tree_html,
)
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.func_text import FuncText
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class AdminMainMenuViewForAdmin(EncodableToWindowData):
    type_: Literal["admin"] = field(init=False, default="admin")
    user_id: int
    user_admin_right_name: AdminRightName
    admin_trees: dict[int, list[int]]
    admin_right_name_map: dict[int, AdminRightName]
    admins_authorized_via_admin_token_count: int
    admins_authorized_via_other_admins_count: int
    admin_count: int

    @classmethod
    def of(  # noqa: PLR0913, PLR0917
        cls,
        user_id: int,
        user_admin_right_name: AdminRightName,
        admin_trees: dict[int, list[int]],
        admin_right_name_map: dict[int, AdminRightName],
        admins_authorized_via_admin_token_count: int,
        admins_authorized_via_other_admins_count: int,
    ) -> "AdminMainMenuViewForAdmin":
        admin_count = (
            admins_authorized_via_admin_token_count
            + admins_authorized_via_other_admins_count
        )

        return AdminMainMenuViewForAdmin(
            user_id=user_id,
            user_admin_right_name=user_admin_right_name,
            admin_trees=admin_trees,
            admin_right_name_map=admin_right_name_map,
            admins_authorized_via_admin_token_count=(
                admins_authorized_via_admin_token_count
            ),
            admins_authorized_via_other_admins_count=(
                admins_authorized_via_other_admins_count
            ),
            admin_count=admin_count,
        )


@dataclass(frozen=True)
class AdminMainMenuViewForNotAdmin(EncodableToWindowData):
    type_: Literal["not_admin"] = field(init=False, default="not_admin")


AdminMainMenuView = AdminMainMenuViewForAdmin | AdminMainMenuViewForNotAdmin


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
async def on_relinquish_admin_right_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
    relinquish_admin_right: FromDishka[RelinquishAdminRight],
) -> None:
    await relinquish_admin_right(callback.from_user.id)


@FuncText
async def admin_trees_text(data: dict[str, Any], _: DialogManager) -> str:  # noqa: RUF029
    return "\n\n".join(
        admin_tree_html(
            parent,
            childs,
            data["main"]["admin_right_name_map"],
            data["main"]["user_id"],
        )
        for parent, childs in data["main"]["admin_trees"].items()
    )


is_admin_f = F["main"]["type_"] == "admin"
is_admin_via_admin_token_f = (
    is_admin_f & F["main"]["user_admin_right_name"] == "via_admin_token"
)

main_window = Window(
    Multi(
        Format(
            "Всего админов {main[admin_count]}"
            " ({main[admins_authorized_via_admin_token_count]}"
            "+{main[admins_authorized_via_other_admins_count]})",
        ),
        Multi(
            Const("Админы:"),
            admin_trees_text,
            when=F["main"]["admin_trees"].len() > 0,
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
        Const("Выдать админ-права"),
        id="authorize_other_user_as_admin",
        state=AdminDialogState.authorize_other_user_as_admin,
        when=is_admin_via_admin_token_f,
    ),
    SwitchTo(
        Const("Забрать админ-права"),
        id="deauthorize_other_user_as_admin",
        state=AdminDialogState.deauthorize_other_user_as_admin,
        when=is_admin_via_admin_token_f,
    ),
    SwitchTo(
        Const("Отказатся от админ-прав"),
        id="relinquish_admin_right",
        state=AdminDialogState.relinquish_admin_right1,
        when=is_admin_f,
    ),

    Multi(
        Const("Вы не админ"),
        Const(" "),
        Const("🧿 Что бы получить права админа введите админ-токен:"),
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
    parse_mode=ParseMode.HTML,
)
