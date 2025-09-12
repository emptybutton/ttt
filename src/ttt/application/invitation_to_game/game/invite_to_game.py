from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import (
    Map,
    NotUniqueActiveInvitationToGameUserIdsError,
)
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.invitation_to_game.game.ports.invitation_to_game_log import (  # noqa: E501
    InvitationToGameLog,
)
from ttt.application.invitation_to_game.game.ports.invitation_to_game_views import (  # noqa: E501
    InvitationToGameViews,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationSelfToGameError,
    invite_to_game,
)
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

            (
                invitation_to_game_id,
                current_datetime,
            ) = await gather(
                self.uuids.random_uuid(),
                self.clock.current_datetime(),
            )

            try:
                tracking = Tracking()
                invitation_to_game = invite_to_game(
                    user,
                    invited_user,
                    invited_user_id,
                    invitation_to_game_id,
                    current_datetime,
                    tracking,
                )
            except InvitationSelfToGameError:
                await self.log.invitation_self_to_game(user)
                await self.views.invitation_self_to_game_view(user)
                return

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
