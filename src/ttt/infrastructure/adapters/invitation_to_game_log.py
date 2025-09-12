from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from structlog.types import FilteringBoundLogger

from ttt.application.invitation_to_game.game.ports.invitation_to_game_log import (
    InvitationToGameLog,
)
from ttt.entities.core.game.game import Game
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
    InvitationToGameState,
)
from ttt.entities.core.user.user import User


def invitation_to_game_state_in_log(state: InvitationToGameState) -> str:
    match state:
        case InvitationToGameState.active:
            return "active"

        case InvitationToGameState.auto_cancelled:
            return "auto_cancelled"

        case InvitationToGameState.cancelled_by_user:
            return "cancelled_by_user"

        case InvitationToGameState.rejected:
            return "rejected"

        case InvitationToGameState.accepted:
            return "accepted"


@dataclass(frozen=True, unsafe_hash=False)
class StructlogInvitationToGameLog(InvitationToGameLog):
    _logger: FilteringBoundLogger

    async def invitation_self_to_game(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "invitation_self_to_game",
            chat_id=user.id,
            user_id=user.id,
        )

    async def user_invited_other_user_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_invited_other_user_to_game",
            chat_id=invitation_to_game.inviting_user.id,
            user_id=invitation_to_game.inviting_user.id,
            invited_user_id=invitation_to_game.invited_user.id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def double_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        await self._logger.ainfo(
            "double_invitation_to_game",
            chat_id=invitation_to_game.inviting_user.id,
            user_id=invitation_to_game.inviting_user.id,
            invited_user_id=invitation_to_game.invited_user.id,
        )

    async def invitation_to_game_is_not_active_to_cancel(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "invitation_to_game_is_not_active_to_cancel",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game.id_,
            invitation_to_game_state=invitation_to_game_state_in_log(
                invitation_to_game.state,
            ),
        )

    async def user_is_not_inviting_user_to_cancel_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_is_not_inviting_user_to_cancel_invitation_to_game",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def invitation_to_game_is_not_active_to_reject(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "invitation_to_game_is_not_active_to_reject",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game.id_,
            invitation_to_game_state=invitation_to_game_state_in_log(
                invitation_to_game.state,
            ),
        )

    async def user_is_not_invited_user_to_reject_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_is_not_invited_user_to_reject_invitation_to_game",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def invitation_to_game_is_not_active_to_accept(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "invitation_to_game_is_not_active_to_accept",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game.id_,
            invitation_to_game_state=invitation_to_game_state_in_log(
                invitation_to_game.state,
            ),
        )

    async def user_is_not_invited_user_to_accept_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_is_not_invited_user_to_accept_invitation_to_game",
            chat_id=user_id,
            user_id=user_id,
            invited_user_id=invitation_to_game.invited_user.id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def users_already_in_game_to_accept_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        users_in_game: Sequence[User],
        /,
    ) -> None:
        await self._logger.ainfo(
            "users_already_in_game_to_accept_invitation_to_game",
            chat_id=invitation_to_game.invited_user.id,
            user_id=invitation_to_game.invited_user.id,
            invitation_to_game_id=invitation_to_game.id_,
            is_invited_user_in_game=(
                invitation_to_game.invited_user in users_in_game
            ),
            is_inviting_user_in_game=(
                invitation_to_game.inviting_user in users_in_game
            ),
        )

    async def user_cancelled_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_cancelled_invitation_to_game",
            chat_id=invitation_to_game.inviting_user.id,
            user_id=invitation_to_game.inviting_user.id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def user_rejected_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_rejected_invitation_to_game",
            chat_id=invitation_to_game.invited_user.id,
            user_id=invitation_to_game.invited_user.id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def user_accepted_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        game: Game,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_accepted_invitation_to_game",
            chat_id=invitation_to_game.invited_user.id,
            user_id=invitation_to_game.invited_user.id,
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def no_invitation_to_game_to_accept(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        await self._logger.ainfo(
            "no_invitation_to_game_to_accept",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game_id,
        )

    async def no_invitation_to_game_to_reject(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        await self._logger.ainfo(
            "no_invitation_to_game_to_reject",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game_id,
        )

    async def no_invitation_to_game_to_cancel(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None:
        await self._logger.ainfo(
            "no_invitation_to_game_to_cancel",
            chat_id=user_id,
            user_id=user_id,
            invitation_to_game_id=invitation_to_game_id,
        )

    async def invitations_to_game_auto_cancelled(
        self,
        ids: Sequence[UUID],
        /,
    ) -> None:
        await gather(*(
            self._logger.ainfo(
                "invitation_to_game_auto_cancelled",
                invitation_to_game_id=invitation_to_game_id,
            )
            for invitation_to_game_id in ids
        ))

    async def no_invitation_to_game_to_auto_cancel(
        self, invitation_to_game_id: UUID, /,
    ) -> None:
        await self._logger.awarning(
            "no_invitation_to_game_to_auto_cancel",
            invitation_to_game_id=invitation_to_game_id,
        )

    async def not_expired_invitation_to_game_to_auto_cancel(
        self, invitation_to_game: InvitationToGame, /,
    ) -> None:
        await self._logger.aerror(
            "not_expired_invitation_to_game_to_auto_cancel",
            invitation_to_game_id=invitation_to_game.id_,
        )

    async def invitation_to_game_state_is_not_active_to_game_to_auto_cancel(
        self, invitation_to_game: InvitationToGame, /,
    ) -> None:
        await self._logger.ainfo(
            "invitation_to_game_state_is_not_active_to_game_to_auto_cancel",
            invitation_to_game_id=invitation_to_game.id_,
        )
