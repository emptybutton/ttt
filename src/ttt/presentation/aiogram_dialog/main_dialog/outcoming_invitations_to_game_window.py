from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from alembic.util import not_none
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.invitation_to_game.game.cancel_invitation_to_game import (
    CancelInvitationToGame,
)
from ttt.application.invitation_to_game.game.invite_to_game import InviteToGame
from ttt.application.invitation_to_game.game.view_outcoming_invitations_to_game import (  # noqa: E501
    ViewOutcomingInvitationsToGame,
)
from ttt.infrastructure.retrier import Retrier
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class OutcomingInvitationToGameData:
    id_hex: str
    invited_user_id: int


@dataclass(frozen=True)
class OutcomingInvitationsToGameView(EncodableToWindowData):
    invitations: list[OutcomingInvitationToGameData]
    need_to_paginate: bool

    @classmethod
    def of(
        cls, invitations: list[OutcomingInvitationToGameData],
    ) -> "OutcomingInvitationsToGameView":
        return OutcomingInvitationsToGameView(
            invitations=invitations,
            need_to_paginate=len(invitations) > 7,  # noqa: PLR2004
        )


@inject
async def getter(
    *,
    event_from_user: User,
    view_invitations: FromDishka[ViewOutcomingInvitationsToGame],
    retrier: FromDishka[Retrier],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await retrier(view_invitations, event_from_user.id)
    view = result_buffer(OutcomingInvitationsToGameView)

    return view.window_data()


@inject
async def on_invitation_selected(
    callback_query: CallbackQuery,
    _: Select[Any],
    __: DialogManager,
    invitation_id_hex: str,
    cancel_invitation_to_game: FromDishka[CancelInvitationToGame],
    retrier: FromDishka[Retrier],
) -> None:
    invitation_id = UUID(hex=invitation_id_hex)
    await retrier(
        cancel_invitation_to_game, callback_query.from_user.id, invitation_id,
    )


@inject
async def input_user_id(
    message: Message,
    _: MessageInput,
    manager: DialogManager,
    invite_to_game: FromDishka[InviteToGame],
    retrier: FromDishka[Retrier],
) -> None:
    try:
        invited_user_id = int(message.text)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {"hint": "👎 ID должен быть целочисленым числом"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
    else:
        await retrier(
            invite_to_game, not_none(message.from_user).id, invited_user_id,
        )


outcoming_invitations_to_game_window = Window(
    Multi(
        Format("{start_data[hint]}"),
        Const(" "),
        when=F["start_data"]["hint"],
    ),
    Const("👤 Введите ID пользователя:"),
    MessageInput(input_user_id, content_types=[ContentType.ANY]),

    Select(
        Format("❌ {item[invited_user_id]}"),
        id="n",
        items=F["main"]["invitations"],
        item_id_getter=lambda it: it["id_hex"],
        on_click=on_invitation_selected,
        when=~F["main"]["need_to_paginate"],
    ),
    ScrollingGroup(
        Select(
            Format("❌ {item[invited_user_id]}"),
            id="n",
            items=F["main"]["invitations"],
            item_id_getter=lambda it: it["id_hex"],
            on_click=on_invitation_selected,
        ),
        width=4,
        height=4,
        id="y",
        when=F["main"]["need_to_paginate"],
    ),

    SwitchTo(
        Const("Назад"),
        id="back",
        state=MainDialogState.game_mode_to_start_game,
    ),
    OneTimekey("hint"),
    state=MainDialogState.outcoming_invitations_to_game,
    getter=getter,
)
