from dataclasses import dataclass

from ttt.application.common.ports.transaction import (
    ReadonlyTransaction,
    SerializableTransaction,
)
from ttt.application.invitation_to_game.game.ports.invitation_to_game_views import (  # noqa: E501
    InvitationToGameViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class ViewOutcomingInvitationsToGame:
    views: InvitationToGameViews
    transaction: ReadonlyTransaction

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            return await self.views.outcoming_user_invitations_to_game_view(
                user_id,
            )
