from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_tasks import GameTasks
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.user.common.ports.user_locks import UserLocks
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.game.game import start_game_with_ai
from ttt.entities.core.user.user import UserAlreadyInGameError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGameWithAi:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    randoms: Randoms
    users: Users
    user_views: CommonUserViews
    games: Games
    game_views: GameViews
    transaction: SerializableTransaction
    ai_gateway: GameAiGateway
    log: GameLog
    tasks: GameTasks
    locks: UserLocks

    async def __call__(self, user_id: int, ai_type: AiType) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        game_id = await self.uuids.random_uuid()
        ai_id = await self.uuids.random_uuid()
        cell_id_matrix = await self.uuids.random_uuid_matrix((3, 3))
        user_emoji = await self.emojis.random_emoji()
        ai_emoji = await self.emojis.random_emoji()
        player_order_random = await self.randoms.random()

        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.user_views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                started_game = start_game_with_ai(
                    cell_id_matrix,
                    game_id,
                    user,
                    user_emoji,
                    ai_id,
                    ai_type,
                    ai_emoji,
                    player_order_random,
                    tracking,
                )
            except UserAlreadyInGameError:
                await self.log.user_already_in_game_to_start_game_against_ai(
                    user,
                )
                await self.transaction.commit()
                await self.game_views.user_already_in_game_view(user_id)
            else:
                await self.log.game_against_ai_started(started_game.game)
                await self.map_(tracking)

                if started_game.next_move_ai_id is not None:
                    await self.locks.lock_user_by_id(user_id)
                    await self.tasks.make_ai_move(
                        user_id,
                        started_game.game.id,
                        started_game.next_move_ai_id,
                    )

                await self.transaction.commit()
                await self.game_views.started_game_view(started_game.game)
