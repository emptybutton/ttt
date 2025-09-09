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


def user_sign(user_admin_right_name: AdminRightName | None) -> str:
    match user_admin_right_name:
        case None:
            return "-"
        case "via_admin_token":
            return "*"
        case "via_other_admin":
            return "#"


def admin_tree_user_id_html(user_id: int, current_user_id: int) -> str:
    trailer = " (Вы)" if user_id == current_user_id else ""
    return f"{Code(user_id).as_html()}{trailer}"


def admin_tree_user_id_title_html(
    user_id: int,
    user_admin_right_name: AdminRightName | None,
    current_user_id: int,
) -> str:
    sign = user_sign(user_admin_right_name)
    id_ = admin_tree_user_id_html(user_id, current_user_id)

    return f"{sign} {id_}"


def admin_tree_html(
    parent: int,
    childs: list[int],
    admin_right_name_map: dict[int, AdminRightName],
    current_user_id: int,
) -> str:
    parent_indetation = " " * 4
    child_indetation = " " * 8

    parent_title = admin_tree_user_id_title_html(
        parent, admin_right_name_map.get(parent), current_user_id,
    )
    parent_part = (
        f"{parent_indetation}{parent_title}:"
        if childs
        else f"{parent_indetation}{parent_title}"
    )

    if not childs:
        return parent_part

    child_part = "\n".join(
        f"""{
            child_indetation
        }{
            admin_tree_user_id_title_html(
                child,
                admin_right_name_map.get(child),
                current_user_id,
            )
        }"""
        for child in childs
    )

    return f"{parent_part}\n{child_part}"
