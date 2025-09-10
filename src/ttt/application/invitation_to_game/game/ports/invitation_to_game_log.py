from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from ttt.entities.core.game.game import Game
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
)
from ttt.entities.core.user.user import User


class InvitationToGameLog(ABC):
    @abstractmethod
    async def invited_user_is_not_registered_to_invite_to_game(
        self,
        user: User,
        invited_user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_invited_other_user_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_is_not_active_to_cancel(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_inviting_user_to_cancel_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_is_not_active_to_reject(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_invited_user_to_reject_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_is_not_active_to_accept(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_invited_user_to_accept_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def users_already_in_game_to_accept_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        users_in_game: Sequence[User],
        /,
    ) -> None: ...

    @abstractmethod
    async def user_cancelled_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_rejected_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_accepted_invitation_to_game(
        self,
        invitation_to_game: InvitationToGame,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_invitation_to_game_to_accept(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None: ...

    @abstractmethod
    async def no_invitation_to_game_to_reject(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None: ...

    @abstractmethod
    async def no_invitation_to_game_to_cancel(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None: ...
