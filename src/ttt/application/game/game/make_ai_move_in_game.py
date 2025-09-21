from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.game.ports.game_dao import GameDao
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    NotAiCurrentMoveError,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class MakeAiMoveInGame:
    map_: Map
    games: Games
    game_views: GameViews
    users: Users
    uuids: UUIDs
    randoms: Randoms
    ai_gateway: GameAiGateway
    transaction: SerializableTransaction
    log: GameLog
    dao: GameDao

    async def __call__(self, game_id: UUID, ai_id: UUID) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            game = await self.games.game_with_id(game_id)

            if game is None:
                await self.log.no_game_to_make_ai_move(game_id)
                return

            (
                free_cell_random,
                ai_move_cell_number_int,
            ) = await gather(
                self.randoms.random(),
                self.ai_gateway.next_move_cell_number_int(game, ai_id),
            )
            try:
                tracking = Tracking()
                ai_move = game.make_ai_move(
                    ai_id,
                    ai_move_cell_number_int,
                    free_cell_random,
                    tracking,
                )
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_make_ai_move(
                    game, ai_id,
                )
            except NotAiCurrentMoveError:
                await self.log.not_ai_current_move_to_make_ai_move(
                    game, ai_id,
                )
            else:
                await self.log.ai_move_maked(game, ai_move, ai_id)

                if game.is_completed():
                    await self.log.game_was_completed_by_ai(ai_id, game)

                await self.map_(tracking)
                await self.transaction.commit()

                await self.game_views.game_view(game)
