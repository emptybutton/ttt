from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.invitation_to_game.game.ports.invitation_to_game_log import (
    InvitationToGameLog,
)
from ttt.application.invitation_to_game.game.ports.invitation_to_game_views import (
    InvitationToGameViews,
)
from ttt.application.invitation_to_game.game.ports.invitations_to_game import (
    InvitationsToGame,
)
from ttt.application.matchmaking_queue.common.matchmaking_queue_log import (
    CommonMatchmakingQueueLog,
)
from ttt.application.matchmaking_queue.common.matchmaking_queue_views import (
    CommonMatchmakingQueueViews,
)
from ttt.application.matchmaking_queue.common.shared_matchmaking_queue import (
    SharedMatchmakingQueue,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGameStateIsNotActiveError,
    UserIsNotInvitedUserError,
    UserIsNotInvitingUserError,
    invite_to_game,
)
from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    UserAlreadyWaitingForGameError,
)
from ttt.entities.core.user.user import UserAlreadyInGameError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RejectInvitationToGame:
    map_: Map
    transaction: Transaction
    views: InvitationToGameViews
    log: InvitationToGameLog
    invitations_to_game: InvitationsToGame

    async def __call__(
        self,
        user_id: int,
        invitation_to_game_id: UUID,
    ) -> None:
        async with self.transaction:
            invitation_to_game = await (
                self.invitations_to_game.invitation_to_game_with_id(
                    invitation_to_game_id,
                )
            )

            if invitation_to_game is None:
                await self.log.no_invitation_to_game_to_reject(
                    user_id, invitation_to_game_id,
                )
                await self.views.no_invitation_to_game_to_reject_view(
                    user_id, invitation_to_game_id,
                )
                return

            try:
                tracking = Tracking()
                invitation_to_game.reject(user_id, tracking)
            except UserIsNotInvitedUserError:
                await (
                    self.log
                    .user_is_not_invited_user_to_reject_invitation_to_game(
                        invitation_to_game, user_id,
                    )
                )
                await (
                    self.views
                    .user_is_not_invited_user_to_reject_invitation_to_game_view(
                        invitation_to_game, user_id,
                    )
                )
            except InvitationToGameStateIsNotActiveError:
                await self.log.invitation_to_game_is_not_active_to_reject(
                    invitation_to_game, user_id,
                )
                await (
                    self.views.invitation_to_game_is_not_active_to_reject_view(
                        invitation_to_game, user_id,
                    )
                )
            else:
                await self.log.user_rejected_invitation_to_game(
                    invitation_to_game,
                )
                await self.map_(tracking)
                await self.views.rejected_invitation_to_game_view(
                    invitation_to_game,
                )
