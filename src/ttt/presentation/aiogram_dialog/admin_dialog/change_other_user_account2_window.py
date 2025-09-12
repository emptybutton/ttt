from dataclasses import dataclass
from functools import partial
from typing import Any, cast

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer, FromDishka
from dishka.integrations.aiogram_dialog import CONTAINER_NAME, inject

from ttt.application.user.change_other_user_account.change_other_user_account import (  # noqa: E501
    ChangeOtherUserAccount,
)
from ttt.application.user.change_other_user_account.set_other_user_account import (  # noqa: E501
    SetOtherUserAccount,
)
from ttt.application.user.change_other_user_account.view_user_account_to_change import (  # noqa: E501
    ViewUserAccountToChange,
)
from ttt.entities.core.stars import Stars
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class ChangeOtherUserAccount2View(EncodableToWindowData):
    other_user_account_stars: Stars


@inject
async def getter(
    *,
    event_from_user: User,
    view_user_account_to_change: FromDishka[ViewUserAccountToChange],
    result_buffer: FromDishka[ResultBuffer],
    dialog_manager: DialogManager,
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    if not isinstance(dialog_manager.start_data, dict):
        raise TypeError

    if "other_user_account_stars" in dialog_manager.start_data:
        stars = dialog_manager.start_data.pop("other_user_account_stars")
        view = ChangeOtherUserAccount2View(stars)
        return view.window_data()

    await view_user_account_to_change(
        event_from_user.id,
        dialog_manager.start_data["other_user_id"],
    )
    view = result_buffer(ChangeOtherUserAccount2View)
    return view.window_data()


@inject
async def input_stars(
    message: Message,
    _: MessageInput,
    manager: DialogManager,
) -> None:
    dishka_container = (
        cast(AsyncContainer, manager.middleware_data[CONTAINER_NAME])
    )

    invalid_format_view = partial(
        manager.start,
        AdminDialogState.authorize_other_user_as_admin,
        {"hint": "Неправильный формат 👎"},
        StartMode.RESET_STACK,
        ShowMode.DELETE_AND_SEND,
    )

    if message.text is None:
        await invalid_format_view()
        return

    try:
        stars = int(message.text.replace(" ", ""))
    except ValueError:
        await invalid_format_view()
        return

    user_id = not_none(message.from_user).id
    other_user_id = cast(dict[str, int], manager.start_data)["other_user_id"]

    match message.text[:1]:
        case "+" | "-":
            change_other_user_account = await dishka_container.get(
                ChangeOtherUserAccount,
            )
            await change_other_user_account(user_id, other_user_id, stars)
        case _:
            set_other_user_account = await dishka_container.get(
                SetOtherUserAccount,
            )
            await set_other_user_account(user_id, other_user_id, stars)


async def on_format_clicked(
    callback: CallbackQuery,
    _: Button,
    __: DialogManager,
) -> None:
    text = (
        "5000 — чтобы счёт был просто 5000 🌟"
        "\n\n+5000 — чтобы счёт увеличился на 5000 🌟"
        "\n\n-5000 — чтобы счёт уменьшился на 5000 🌟"
    )
    await callback.answer(text, show_alert=True)


change_other_user_account2_window = Window(
    Format("На счёту пользователя {main[other_user_account_stars]} 🌟"),
    hint(key="hint"),
    Const(" "),
    Const("🧿 Введите звёзды:"),
    MessageInput(
        input_stars,
        content_types=[ContentType.ANY],
    ),

    Row(
        Button(Const("Формат"), id="format", on_click=on_format_clicked),
        SwitchTo(
            Const("Назад"),
            id="back",
            state=AdminDialogState.change_other_user_account1,
        ),
    ),

    OneTimekey("hint"),
    state=AdminDialogState.change_other_user_account2,
    getter=getter,
)
