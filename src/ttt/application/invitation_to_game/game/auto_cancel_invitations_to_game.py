from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.transaction import Transaction
from ttt.application.invitation_to_game.game.ports.invitation_to_game_dao import (  # noqa: E501
    InvitationToGameDao,
)
from ttt.application.invitation_to_game.game.ports.invitation_to_game_log import (  # noqa: E501
    InvitationToGameLog,
)
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    invitation_to_game_datetime,
)


@dataclass(frozen=True, unsafe_hash=False)
class AutoCancelInvitationsToGame:
    transaction: Transaction
    log: InvitationToGameLog
    clock: Clock
    invitation_to_game_dao: InvitationToGameDao

    async def __call__(self) -> None:
        async with self.transaction:
            expiration_datetime = await self.clock.current_datetime()
            auto_cancelled_invitations_to_game_ids = await (
                self.invitation_to_game_dao
                .set_auto_cancelled_where_invitation_datetime_le_and_active(
                    invitation_to_game_datetime(expiration_datetime),
                )
            )
            await self.log.invitations_to_game_auto_cancelled(
                auto_cancelled_invitations_to_game_ids,
            )
