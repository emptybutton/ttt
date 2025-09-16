from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
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
from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    UserAlreadyWaitingForGameError,
)
from ttt.entities.core.user.user import UserAlreadyInGameError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    transaction: Transaction
    clock: Clock
    users: Users
    user_views: CommonUserViews
    games: Games
    game_views: GameViews
    game_log: GameLog
    shared_matchmaking_queue: SharedMatchmakingQueue
    matchmaking_queue_views: CommonMatchmakingQueueViews
    matchmaking_queue_log: CommonMatchmakingQueueLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.user_views.user_is_not_registered_view(user_id)
                return

            matchmaking_queue = await self.shared_matchmaking_queue
            user_waiting_id = await self.uuids.random_uuid()
            game_id = await self.uuids.random_uuid()
            cell_id_matrix = await self.uuids.random_uuid_matrix((3, 3))
            user1_emoji = await self.emojis.random_emoji()
            user2_emoji = await self.emojis.random_emoji()
            current_datetime = await self.clock.current_datetime()

            try:
                tracking = Tracking()
                game = matchmaking_queue.add_user(
                    user,
                    user_waiting_id,
                    cell_id_matrix,
                    game_id,
                    user1_emoji,
                    user2_emoji,
                    current_datetime,
                    tracking,
                )
            except UserAlreadyWaitingForGameError:
                await self.matchmaking_queue_log.double_waiting_for_game_start(
                    user_id,
                )
                await self.matchmaking_queue_views.double_waiting_for_game_view(
                    user_id,
                )
            except UserAlreadyInGameError:
                await (
                    self.matchmaking_queue_log
                    .user_already_in_game_to_add_to_matchmaking_queue(user_id)
                )
                await self.game_views.user_already_in_game_view(user_id)
            else:
                if game is None:
                    await self.matchmaking_queue_log.waiting_for_game_start(
                        user_id,
                    )
                    await self.matchmaking_queue_views.waiting_for_game_view(
                        user_id,
                    )
                    await self.map_(tracking)
                    return

                await self.game_log.game_against_user_started(game)
                await self.map_(tracking)

                await self.game_views.started_game_view(game)
