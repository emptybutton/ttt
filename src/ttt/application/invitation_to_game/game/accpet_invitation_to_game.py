from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
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
from ttt.entities.core.game.game import UsersAlreadyInGameError
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
class AcceptInvitationToGame:
    map_: Map
    transaction: Transaction
    views: InvitationToGameViews
    log: InvitationToGameLog
    invitations_to_game: InvitationsToGame
    emojis: Emojis
    uuids: UUIDs
    randoms: Randoms

    async def __call__(
        self,
        user_id: int,
        invitation_to_game_id: UUID,
    ) -> None:
        async with self.transaction:
            (
                invitation_to_game,
                user_random_emoji,
                inviting_player_random_emoji,
                player_order_random,
                cell_id_matrix,
                game_id,
            ) = await gather(
                self.invitations_to_game.invitation_to_game_with_id(
                    invitation_to_game_id,
                ),
                self.emojis.random_emoji(),
                self.emojis.random_emoji(),
                self.randoms.random(),
                self.uuids.random_uuid_matrix((3, 3)),
                self.uuids.random_uuid(),
            )

            if invitation_to_game is None:
                await self.log.no_invitation_to_game_to_accept(
                    user_id, invitation_to_game_id,
                )
                await self.views.no_invitation_to_game_to_accept_view(
                    user_id, invitation_to_game_id,
                )
                return

            try:
                tracking = Tracking()
                game = invitation_to_game.accept(
                    user_id,
                    user_random_emoji,
                    inviting_player_random_emoji,
                    player_order_random,
                    cell_id_matrix,
                    game_id,
                    tracking,
                )
            except UserIsNotInvitedUserError:
                await (
                    self.log
                    .user_is_not_invited_user_to_accept_invitation_to_game(
                        invitation_to_game, user_id,
                    )
                )
                await (
                    self.views
                    .user_is_not_invited_user_to_accept_invitation_to_game_view(
                        invitation_to_game, user_id,
                    )
                )
            except InvitationToGameStateIsNotActiveError:
                await self.log.invitation_to_game_is_not_active_to_accept(
                    invitation_to_game, user_id,
                )
                await (
                    self.views.invitation_to_game_is_not_active_to_accept_view(
                        invitation_to_game, user_id,
                    )
                )
            except UsersAlreadyInGameError as error:
                await (
                    self.log.users_already_in_game_to_accept_invitation_to_game(
                        invitation_to_game, error.users,
                    )
                )
                await (
                    self.views
                    .users_already_in_game_to_accept_invitation_to_game_view(
                        invitation_to_game, error.users,
                    )
                )
            else:
                await self.log.user_accepted_invitation_to_game(
                    invitation_to_game, game,
                )
                await self.map_(tracking)
                await self.views.accepted_invitation_to_game_view(
                    invitation_to_game, game,
                )
