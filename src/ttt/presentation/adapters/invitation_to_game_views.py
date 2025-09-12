from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast
from uuid import UUID

from aiogram.types import CallbackQuery
from aiogram.utils.formatting import Code, Text
from aiogram_dialog import DialogManager, ShowMode, StartMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.invitation_to_game.game.ports.invitation_to_game_views import (  # noqa: E501
    InvitationToGameViews,
)
from ttt.entities.core.game.game import Game
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
    InvitationToGameState,
)
from ttt.entities.core.user.user import User
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.sqlalchemy.tables.invitation_to_game import (
    TableInvitationToGame,
    TableInvitationToGameState,
)
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.game_window import (
    ActiveGameView,
)
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitation_to_game_window import (  # noqa: E501
    IncomingInvitationToGameView,
)
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitations_to_game_window import (  # noqa: E501
    IncomingInvitationsToGameView,
    IncomingInvitationToGameData,
)
from ttt.presentation.aiogram_dialog.main_dialog.outcoming_invitations_to_game_window import (  # noqa: E501
    OutcomingInvitationsToGameView,
    OutcomingInvitationToGameData,
)
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True, unsafe_hash=False)
class AiogramInvitationToGameViews(InvitationToGameViews):
    _session: AsyncSession
    _callback_query: CallbackQuery | None
    _dialog_manager_for_user: DialogManagerForUser
    _result_buffer: ResultBuffer

    async def incoming_user_invitations_to_game_view(
        self,
        user_id: int,
        /,
    ) -> None:
        stmt = (
            select(
                TableInvitationToGame.id,
                TableInvitationToGame.inviting_user_id,
            )
            .where(
                (TableInvitationToGame.invited_user_id == user_id)
                & (
                    TableInvitationToGame.state
                    == TableInvitationToGameState.active.value
                ),
            )
        )
        result = await self._session.execute(stmt)
        rows = result.all()

        invitations = [
            IncomingInvitationToGameData(row.id, row.inviting_user_id)
            for row in rows
        ]
        self._result_buffer.result = IncomingInvitationsToGameView.of(
            invitations,
        )

    async def outcoming_user_invitations_to_game_view(
        self,
        user_id: int,
        /,
    ) -> None:
        stmt = (
            select(
                TableInvitationToGame.id,
                TableInvitationToGame.invited_user_id,
            )
            .where(
                (TableInvitationToGame.inviting_user_id == user_id)
                & (
                    TableInvitationToGame.state
                    == TableInvitationToGameState.active.value
                ),
            )
        )
        result = await self._session.execute(stmt)
        rows = result.all()

        invitations = [
            OutcomingInvitationToGameData(row.id.hex, row.invited_user_id)
            for row in rows
        ]
        self._result_buffer.result = OutcomingInvitationsToGameView.of(
            invitations,
        )

    async def one_incoming_invitation_to_game_view(
        self, user_id: int, /,
    ) -> None:
        stmt = (
            select(
                TableInvitationToGame.id,
                TableInvitationToGame.inviting_user_id,
            )
            .where(
                (TableInvitationToGame.invited_user_id == user_id)
                & (
                    TableInvitationToGame.state
                    == TableInvitationToGameState.active.value
                ),
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            self._result_buffer.result = None
            return

        self._result_buffer.result = IncomingInvitationToGameView(
            id_hex=row.id.hex,
            inviting_user_id=row.inviting_user_id,
        )

    async def incoming_invitation_to_game_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        stmt = (
            select(TableInvitationToGame.inviting_user_id)
            .where(
                (TableInvitationToGame.id == invitation_to_game_id)
                & (
                    TableInvitationToGame.state
                    == TableInvitationToGameState.active.value
                ),
            )
        )
        inviting_user_id = await self._session.scalar(stmt)

        if inviting_user_id is None:
            self._result_buffer.result = None
            return

        self._result_buffer.result = IncomingInvitationToGameView(
            id_hex=invitation_to_game_id.hex,
            inviting_user_id=inviting_user_id,
        )

    async def invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(
            invitation_to_game.inviting_user.id,
        )
        await gather(
            manager.start(
                MainDialogState.outcoming_invitations_to_game,
                {},
                StartMode.RESET_STACK,
                ShowMode.DELETE_AND_SEND,
            ),
            self._invited_user_to_game_view(invitation_to_game),
        )

    async def _invited_user_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        if invitation_to_game.invited_user.is_in_game():
            return

        manager = self._dialog_manager_for_user(
            invitation_to_game.invited_user.id,
        )
        view = IncomingInvitationToGameView(
            id_hex=invitation_to_game.id_.hex,
            inviting_user_id=invitation_to_game.inviting_user.id,
        )
        start_data = view.window_data()
        await manager.start(
            MainDialogState.incoming_invitation_to_game,
            start_data,
        )

    async def cancelled_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(invitation_to_game.inviting_user.id)
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def rejected_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        invited_user_manager = cast(
            DialogManager,
            self._dialog_manager_for_user(invitation_to_game.invited_user.id),
        )
        inviting_user_manager = self._dialog_manager_for_user(
            invitation_to_game.inviting_user.id,
        )

        inviting_user_hint = Text(
            "👤 Пользователь ",
            Code(invitation_to_game.invited_user.id),
            " отклонил ваше приглашение к игре",
        ).as_html()

        await gather(
            invited_user_manager.done(),
            inviting_user_manager.start(
                MainDialogState.notification,
                {"hint": inviting_user_hint},
            ),
        )

    async def accepted_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        game: Game,
        /,
    ) -> None:
        await gather(
            self._active_game_view(game, invitation_to_game.invited_user.id),
            self._active_game_view(game, invitation_to_game.inviting_user.id),
        )

    async def invitation_self_to_game_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {"hint": "😭 Вы не можете пригласить самого себя"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def double_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(
            invitation_to_game.inviting_user.id,
        )
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {"hint": "👎 Пользователь уже приглашён в игру"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def invitation_to_game_is_not_active_to_cancel_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def user_is_not_inviting_user_to_cancel_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def invitation_to_game_is_not_active_to_reject_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        manager = cast(
            DialogManager,
            self._dialog_manager_for_user(invitation_to_game.invited_user.id),
        )
        await manager.done()

    async def user_is_not_invited_user_to_reject_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        manager = cast(DialogManager, self._dialog_manager_for_user(user_id))
        await manager.done()

    async def invitation_to_game_is_not_active_to_accept_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        match invitation_to_game.state:
            case (
                InvitationToGameState.auto_cancelled
                | InvitationToGameState.cancelled_by_user
            ):
                text = "Приглашение уже отменено"
            case InvitationToGameState.rejected:
                text = "Приглашение уже отклонено"
            case InvitationToGameState.accepted:
                return
            case InvitationToGameState.active:
                raise ValueError

        callback_query = not_none(self._callback_query)
        await callback_query.answer(text, show_alert=True)

    async def users_already_in_game_to_accept_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        users_in_game: Sequence[User],
        /,
    ) -> None:
        if invitation_to_game.invited_user in users_in_game:
            text = "Закончите игру, прежде чем начинать новую"
        elif invitation_to_game.inviting_user in users_in_game:
            text = "Пользователь в игре, подождите пока игра закончится"
        else:
            raise ValueError

        callback_query = not_none(self._callback_query)
        await callback_query.answer(text, show_alert=True)

    async def user_is_not_invited_user_to_accept_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        ...

    async def no_invitation_to_game_to_accept_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        ...

    async def no_invitation_to_game_to_reject_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        manager = cast(DialogManager, self._dialog_manager_for_user(user_id))
        await manager.done()

    async def no_invitation_to_game_to_cancel_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def _active_game_view(self, game: Game, user_id: int) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        view = ActiveGameView.of(game, user_id)
        data = view.window_data()

        await dialog_manager.start(
            MainDialogState.game, data, StartMode.RESET_STACK,
        )
