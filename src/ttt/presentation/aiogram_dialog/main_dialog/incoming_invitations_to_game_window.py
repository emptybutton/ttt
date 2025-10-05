from dataclasses import dataclass
from typing import Any
from uuid import UUID

from aiogram.types import CallbackQuery, User
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import (
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.invitation_to_game.game.view_incoming_invitation_to_game import (  # noqa: E501
    ViewIncomingInvitationToGame,
)
from ttt.application.invitation_to_game.game.view_incoming_invitations_to_game import (  # noqa: E501
    ViewIncomingInvitationsToGame,
)
from ttt.infrastructure.retrier import Retrier
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.func_text import FuncText
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitation_to_game_window import (  # noqa: E501
    IncomingInvitationToGameView,
)
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class IncomingInvitationToGameData:
    id_hex: str
    inviting_user_id: int
    inviting_user_username: str | None


@dataclass(frozen=True)
class IncomingInvitationsToGameView(EncodableToWindowData):
    invitations: list[IncomingInvitationToGameData]

    @classmethod
    def of(
        cls, invitations: list[IncomingInvitationToGameData],
    ) -> "IncomingInvitationsToGameView":
        return IncomingInvitationsToGameView(invitations=invitations)


@inject
async def getter(
    *,
    event_from_user: User,
    view_invitations: FromDishka[ViewIncomingInvitationsToGame],
    retrier: FromDishka[Retrier],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await retrier(view_invitations, event_from_user.id)
    view = result_buffer(IncomingInvitationsToGameView)

    return view.window_data()


@inject
async def on_invitation_selected(  # noqa: PLR0913, PLR0917
    callback_query: CallbackQuery,
    _: Select[Any],
    manager: DialogManager,
    invitation_id_hex: str,
    view_invitation_to_game: FromDishka[ViewIncomingInvitationToGame],
    retrier: FromDishka[Retrier],
    result_buffer: FromDishka[ResultBuffer],
) -> None:
    invitation_id = UUID(hex=invitation_id_hex)
    await retrier(
        view_invitation_to_game, callback_query.from_user.id, invitation_id,
    )
    view = result_buffer.result

    if not isinstance(view, IncomingInvitationToGameView | None):
        raise TypeError

    if view is None:
        await manager.start(
            MainDialogState.main,
            {"hint": "😭 Предложение отклонено"},
            StartMode.RESET_STACK,
        )
        return

    start_data = view.window_data()
    await manager.start(MainDialogState.incoming_invitation_to_game, start_data)


async def incoming_invitations_to_game_text(  # noqa: RUF029
    data: dict[str, Any],
    _: DialogManager,
) -> str:
    return f"👥 У вас {len(data["main"]["invitations"])} приглашений к игре"


async def incoming_invitation_to_game_text(  # noqa: RUF029
    data: dict[str, Any],
    _: DialogManager,
) -> str:
    invitation = data["item"]

    if invitation.get("inviting_user_username") is None:
        return f"От {invitation["inviting_user_id"]}"

    return f"От @{invitation["inviting_user_username"]}"


incoming_invitations_to_game_window = Window(
    FuncText(incoming_invitations_to_game_text),
    ScrollingGroup(
        Select(
            FuncText(incoming_invitation_to_game_text),
            id="n",
            items=F["main"]["invitations"],
            item_id_getter=lambda it: it["id_hex"],
            on_click=on_invitation_selected,
        ),
        width=2,
        height=2,
        hide_on_single_page=True,
        id="y",
    ),

    SwitchTo(
        Const("Назад"),
        id="back",
        state=MainDialogState.main,
    ),
    state=MainDialogState.incoming_invitations_to_game,
    getter=getter,
)
