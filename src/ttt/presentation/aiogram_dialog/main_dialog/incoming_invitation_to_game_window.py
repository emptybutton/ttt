from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.utils.formatting import Code, Text
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Row,
)
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.invitation_to_game.game.accpet_invitation_to_game import (
    AcceptInvitationToGame,
)
from ttt.application.invitation_to_game.game.reject_invitation_to_game import (
    RejectInvitationToGame,
)
from ttt.infrastructure.retrier import Retrier
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.func_text import FuncText
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@dataclass(frozen=True)
class IncomingInvitationToGameView(EncodableToWindowData):
    id_hex: str
    inviting_user_id: int


@inject
async def on_accept_clicked(
    callback: CallbackQuery,
    _: Button,
    manager: DialogManager,
    accept_invitation_to_game: FromDishka[AcceptInvitationToGame],
    retrier: FromDishka[Retrier],
) -> None:
    if not isinstance(manager.start_data, dict):
        raise TypeError

    invitation_id = UUID(hex=manager.start_data["main"]["id_hex"])
    await retrier(
        accept_invitation_to_game, callback.from_user.id, invitation_id,
    )


@inject
async def on_reject_clicked(
    callback: CallbackQuery,
    _: Button,
    manager: DialogManager,
    reject_invitation_to_game: FromDishka[RejectInvitationToGame],
    retrier: FromDishka[Retrier],
) -> None:
    if not isinstance(manager.start_data, dict):
        raise TypeError

    invitation_id = UUID(hex=manager.start_data["main"]["id_hex"])
    await retrier(
        reject_invitation_to_game, callback.from_user.id, invitation_id,
    )


async def incoming_invitation_to_game_html(  # noqa: RUF029
    _: dict[str, Any],
    manager: DialogManager,
) -> str:
    if not isinstance(manager.start_data, dict):
        raise TypeError

    invitation = manager.start_data["main"]
    text = Text(
        "👤 Приглашение к игре от ", Code(invitation["inviting_user_id"]),
    )
    return text.as_html()


incoming_invitation_to_game_window = Window(
    hint(key="hint"),
    FuncText(incoming_invitation_to_game_html, when=~F["start_data"]["hint"]),
    Row(
        Button(Const("Принять"), id="accept", on_click=on_accept_clicked),
        Button(Const("Отклонить"), id="reject", on_click=on_reject_clicked),
        when=~F["start_data"]["hint"],
    ),
    Cancel(Const("Назад")),

    OneTimekey("hint"),
    state=MainDialogState.incoming_invitation_to_game,
    parse_mode=ParseMode.HTML,
)
