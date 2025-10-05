from dataclasses import dataclass
from typing import Any, cast
from uuid import UUID

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    KeyboardButtonRequestUsers,
    Message,
    User,
)
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    ListGroup,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
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
from ttt.presentation.aiogram_dialog.common.wigets.func_text import FuncText
from ttt.presentation.aiogram_dialog.common.wigets.hint import hint
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.common.wigets.users_request import (
    UsersRequest,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True)
class OutcomingInvitationToGameData:
    id_hex: str
    invited_user_id: int
    invited_user_username: str | None


@dataclass(frozen=True)
class OutcomingInvitationsToGameView(EncodableToWindowData):
    invitations: list[OutcomingInvitationToGameData]

    @classmethod
    def of(
        cls, invitations: list[OutcomingInvitationToGameData],
    ) -> "OutcomingInvitationsToGameView":
        return OutcomingInvitationsToGameView(invitations=invitations)


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
async def input_user(
    message: Message,
    _: MessageInput,
    __: DialogManager,
    invite_to_game: FromDishka[InviteToGame],
    retrier: FromDishka[Retrier],
) -> None:
    if message.users_shared is None:
        return

    user = not_none(message.from_user)
    shared_user = message.users_shared.users[0]

    await retrier(
        invite_to_game,
        user.id,
        user.username,
        shared_user.user_id,
        shared_user.username,
    )


async def title_text(  # noqa: RUF029
    data: dict[str, Any],
    _: DialogManager,
) -> str:
    if data["main"]["invitations"]:
        return f"👤 Приглашено {len(data["main"]["invitations"])}"

    return "👤 Никто не приглашён"


async def invitation_text(  # noqa: RUF029
    data: dict[str, Any],
    _: DialogManager,
) -> str:
    invited_user_id = data["item"]["invited_user_id"]
    invited_user_username = data["item"].get("invited_user_username")

    if invited_user_username is None:
        return f"➖ {invited_user_id}"

    return f"➖ @{invited_user_username}"


outcoming_invitations_to_game_window = Window(
    hint(key="hint"),
    FuncText(title_text, when=~F["start_data"]["hint"]),

    Group(
        Select(
            FuncText(invitation_text),
            id="n",
            items=F["main"]["invitations"],
            item_id_getter=lambda it: it["id_hex"],
            on_click=on_invitation_selected,
        ),
        id="l",
        width=1,
    ),
    UsersRequest(
        Const("➕ Пригласить"),
        id="invite_to_game",
        criteria=KeyboardButtonRequestUsers(
            request_id=4,
            user_is_bot=False,
            request_name=False,
            request_username=True,
            request_photo=False,
        ),
    ),
    MessageInput(input_user, content_types=[ContentType.ANY]),

    SwitchTo(
        Const("Назад"),
        id="back",
        state=MainDialogState.game_mode_to_start_game,
    ),
    OneTimekey("hint"),
    markup_factory=ReplyKeyboardFactory(resize_keyboard=True),
    state=MainDialogState.outcoming_invitations_to_game,
    getter=getter,
)
