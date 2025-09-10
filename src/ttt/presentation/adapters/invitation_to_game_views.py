from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast
from uuid import UUID

from aiogram_dialog import DialogManager, StartMode
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
from ttt.infrastructure.sqlalchemy.tables.invitation_to_game import TableInvitationToGame, TableInvitationToGameState
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.game_window import ActiveGameView
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitations_to_game_window import IncomingInvitationToGameData, IncomingInvitationsToGameView
from ttt.presentation.aiogram_dialog.main_dialog.outcoming_invitations_to_game_window import OutcomingInvitationToGameData, OutcomingInvitationsToGameView
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True, unsafe_hash=False)
class AiogramInvitationToGameViews(InvitationToGameViews):
    _session: AsyncSession
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
            ).where(
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
            ).where(
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
            OutcomingInvitationToGameData(row.id, row.invited_user_id)
            for row in rows
        ]
        self._result_buffer.result = OutcomingInvitationsToGameView.of(
            invitations,
        )

    async def invited_user_is_not_registered_to_invite_to_game_view(
        self,
        user: User,
        invited_user_id: int,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            MainDialogState.outcoming_invitations_to_game,
            {"hint": "Пользователь не зарегестрирован 👎"},
            StartMode.RESET_STACK,
        )

    async def invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    async def cancelled_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    async def rejected_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

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
            {"hint": "Пользователь уже приглашён в игру 👎"},
            StartMode.RESET_STACK,
        )

    async def invitation_to_game_is_not_active_to_cancel_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        ...

    async def user_is_not_inviting_user_to_cancel_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        raise NotImplementedError

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
        await manager.back()

    async def user_is_not_invited_user_to_reject_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        raise NotImplementedError

    async def invitation_to_game_is_not_active_to_accept_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)

        match invitation_to_game.state:
            case (
                InvitationToGameState.auto_cancelled
                | InvitationToGameState.cancelled_by_user
            ):
                hint = "Приглашение уже отменено"
            case InvitationToGameState.rejected:
                hint = "Приглашение уже отклонено"
            case InvitationToGameState.accepted:
                return
            case InvitationToGameState.active:
                raise ValueError

        await manager.start(
            MainDialogState.incoming_invitations_to_game,
            {"hint": hint},
            StartMode.RESET_STACK,
        )

    async def users_already_in_game_to_accept_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        users_in_game: Sequence[User],
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(
            invitation_to_game.invited_user.id,
        )

        if (
            invitation_to_game.invited_user in users_in_game
            and invitation_to_game.inviting_user in users_in_game
        ):
            hint = "Вы в игре и пользователь в игре чтобы начать игру"

        await manager.start(
            MainDialogState.incoming_invitations_to_game,
            {"hint": "Пользователь уже приглашён в игру 👎"},
            StartMode.RESET_STACK,
        )

    async def user_is_not_invited_user_to_accept_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        raise NotImplementedError

    async def no_invitation_to_game_to_accept_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        raise NotImplementedError

    async def no_invitation_to_game_to_reject_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        raise NotImplementedError

    async def no_invitation_to_game_to_cancel_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        raise NotImplementedError

    async def _active_game_view(self, game: Game, user_id: int) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        view = ActiveGameView.of(game, user_id)
        data = view.window_data()

        await dialog_manager.start(
            MainDialogState.game, data, StartMode.RESET_STACK,
        )
