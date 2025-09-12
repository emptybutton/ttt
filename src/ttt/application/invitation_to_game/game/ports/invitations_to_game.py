from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
)


class InvitationsToGame(ABC):
    @abstractmethod
    async def invitation_to_game_with_id(
        self, id_: UUID, /,
    ) -> InvitationToGame | None: ...
