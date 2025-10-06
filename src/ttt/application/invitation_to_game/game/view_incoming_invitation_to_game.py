from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.transaction import (
    ReadonlyTransaction,
)
from ttt.application.invitation_to_game.game.ports.invitation_to_game_views import (  # noqa: E501
    InvitationToGameViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class ViewIncomingInvitationToGame:
    views: InvitationToGameViews
    transaction: ReadonlyTransaction

    async def __call__(self, user_id: int, invitation_to_game_id: UUID) -> None:
        async with self.transaction:
            return await self.views.incoming_invitation_to_game_view(
                user_id, invitation_to_game_id,
            )
