from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from ttt.entities.core.game.game import Game
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
)
from ttt.entities.core.user.user import User


class InvitationToGameViews(ABC):
    @abstractmethod
    async def incoming_user_invitations_to_game_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def outcoming_user_invitations_to_game_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invited_user_is_not_registered_to_invite_to_game_view(
        self,
        user: User,
        invited_user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def cancelled_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def rejected_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def accepted_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_is_not_active_to_cancel_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_inviting_user_to_cancel_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_is_not_active_to_reject_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_invited_user_to_reject_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invitation_to_game_is_not_active_to_accept_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def users_already_in_game_to_accept_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        users_in_game: Sequence[User],
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_invited_user_to_accept_invitation_to_game_view(
        self,
        invitation_to_game: InvitationToGame,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_invitation_to_game_to_accept_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None: ...

    @abstractmethod
    async def no_invitation_to_game_to_reject_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None: ...

    @abstractmethod
    async def no_invitation_to_game_to_cancel_view(
        self, user_id: int, invitation_to_game_id: UUID, /,
    ) -> None: ...
