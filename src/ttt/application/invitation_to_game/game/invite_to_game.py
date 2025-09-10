from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import (
    Map,
    NotUniqueActiveInvitationToGameUserIdsError,
)
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
    invite_to_game,
)
from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    UserAlreadyWaitingForGameError,
)
from ttt.entities.core.user.user import UserAlreadyInGameError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class InviteToGame:
    map_: Map
    uuids: UUIDs
    transaction: Transaction
    clock: Clock
    users: Users
    user_views: CommonUserViews
    views: InvitationToGameViews
    log: InvitationToGameLog

    async def __call__(self, user_id: int, invited_user_id: int) -> None:
        async with self.transaction:
            user, invited_user = await self.users.users_with_ids(
                (user_id, invited_user_id),
            )

            if user is None:
                await self.user_views.user_is_not_registered_view(user_id)
                return

            if invited_user is None:
                await self.log.invited_user_is_not_registered_to_invite_to_game(
                    user, invited_user_id,
                )
                await (
                    self.views
                    .invited_user_is_not_registered_to_invite_to_game_view(
                        user, invited_user_id,
                    )
                )
                return

            invitation_to_game_id, current_datetime = gather(
                self.uuids.random_uuid(),
                self.clock.current_datetime(),
            )

            tracking = Tracking()
            invitation_to_game = invite_to_game(
                user,
                invited_user,
                invitation_to_game_id,
                current_datetime,
                tracking,
            )

            try:
                await self.map_(tracking)
            except NotUniqueActiveInvitationToGameUserIdsError:
                await self.log.double_invitation_to_game(invitation_to_game)
                await self.views.double_invitation_to_game_view(
                    invitation_to_game,
                )
            else:
                await self.log.user_invited_other_user_to_game(
                    invitation_to_game,
                )
                await self.views.invitation_to_game_view(invitation_to_game)
