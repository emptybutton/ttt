from typing import Literal

from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import Code
from aiogram_dialog.widgets.text import Jinja

from ttt.entities.core.user.admin_right import (
    AdminRight,
    AdminRightViaAdminToken,
    AdminRightViaOtherAdmin,
)
from itertools import starmap


class AdminDialogState(StatesGroup):
    main = State()
    other_user_profile = State()
    relinquish_admin_right1 = State()
    relinquish_admin_right2 = State()
    authorize_other_user_as_admin = State()
    deauthorize_other_user_as_admin = State()


type AdminRightName = Literal["via_admin_token", "via_other_admin"]


def admin_right_name(admin_right: AdminRight | None) -> AdminRightName | None:
    match admin_right:
        case AdminRightViaAdminToken():
            return "via_admin_token"
        case AdminRightViaOtherAdmin():
            return "via_other_admin"
        case None:
            return None


def admin_tree_html(
    parent: int,
    parent_admin_right: AdminRight | None,
    childs: list[int],
    current_user_id: int,
) -> str:
    match parent_admin_right:
        case None:
            parent_sing = "X"
        case AdminRightViaAdminToken():
            parent_sing = "*"
        case AdminRightViaOtherAdmin():
            parent_sing = "#"

    parent_part = (
        f"   {parent_sing} {admin_tree_user_id_html(parent, current_user_id)}:"
        if childs
        else f"   * {admin_tree_user_id_html(parent, current_user_id)}"
    )
    child_part = "\n".join(
        f"      # {admin_tree_user_id_html(child, current_user_id)}"
        for child in childs
    )
    return f"{parent_part}\n{child_part}" if child_part else parent_part


def admin_tree_user_id_html(user_id: int, current_user_id: int) -> str:
    trailer = " (Вы)" if user_id == current_user_id else ""
    return f"{Code(user_id).as_html()}{trailer}"
