from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_starting_queue import (
    GameStartingQueue,
)
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.game.game import start_game_with_ai
from ttt.entities.core.user.location import UserLocation
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
    game_starting_queue: GameStartingQueue
    transaction: Transaction
    ai_gateway: GameAiGateway
    log: GameLog

    async def __call__(self, location: UserLocation, ai_type: AiType) -> None:
        game_id = await self.uuids.random_uuid()
        ai_id = await self.uuids.random_uuid()
        cell_id_matrix = await self.uuids.random_uuid_matrix((3, 3))
        user_emoji = await self.emojis.random_emoji()
        ai_emoji = await self.emojis.random_emoji()
        player_order_random = await self.randoms.random()

        async with self.transaction:
            user = await self.users.user_with_id(location.user_id)

            if user is None:
                await self.user_views.user_is_not_registered_view(
                    location,
                )
                return

            try:
                tracking = Tracking()
                started_game = start_game_with_ai(
                    cell_id_matrix,
                    game_id,
                    user,
                    user_emoji,
                    location.chat_id,
                    ai_id,
                    ai_type,
                    ai_emoji,
                    player_order_random,
                    tracking,
                )
            except UserAlreadyInGameError:
                await self.log.user_already_in_game_to_start_game(
                    user,
                    location,
                )
                await self.game_views.user_already_in_game_views(
                    [location],
                )
            else:
                await self.log.game_against_ai_started(started_game.game)

                if started_game.next_move_ai_id is None:
                    await self.map_(tracking)
                    await self.game_views.started_game_view_with_locations(
                        [location.game(started_game.game.id)],
                        started_game.game,
                    )
                else:
                    await self.game_views.started_game_view_with_locations(
                        [location.game(started_game.game.id)],
                        started_game.game,
                    )

                    game_result_id = await self.uuids.random_uuid()
                    free_cell_random = await self.randoms.random()
                    ai_move_cell_number_int = (
                        await self.ai_gateway.next_move_cell_number_int(
                            started_game.game,
                            started_game.next_move_ai_id,
                        )
                    )
                    ai_move = started_game.game.make_ai_move(
                        started_game.next_move_ai_id,
                        ai_move_cell_number_int,
                        game_result_id,
                        free_cell_random,
                        tracking,
                    )
                    await self.log.ai_move_maked(
                        location,
                        started_game.game,
                        ai_move,
                    )

                    await self.map_(tracking)
                    await self.game_views.game_view_with_locations(
                        [location.game(started_game.game.id)],
                        started_game.game,
                    )
