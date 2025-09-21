from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.game.ports.game_dao import GameDao
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_tasks import GameTasks
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.cell import AlreadyFilledCellError
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    NoCellError,
    NotCurrentPlayerError,
)
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class MakeMoveInGame:
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
    tasks: GameTasks

    async def __call__(
        self,
        user_id: int,
        cell_number_int: int,
    ) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            game = await self.games.current_user_game(user_id)

            if game is None:
                await self.game_views.no_current_game_view(user_id)
                return

            (
                random,
                games_played_by_player_id,
            ) = await gather(
                self.randoms.random(),
                self.dao.games_played_by_player_id(game),
            )

            try:
                tracking = Tracking()
                user_move = game.make_user_move(
                    user_id,
                    cell_number_int,
                    games_played_by_player_id,
                    random,
                    tracking,
                )
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_make_move(
                    game,
                    user_id,
                    cell_number_int,
                )
                await self.transaction.commit()
                await self.game_views.game_already_complteted_view(
                    user_id,
                    game,
                )
            except NotCurrentPlayerError:
                await self.log.not_current_player_to_make_move(
                    game,
                    user_id,
                    cell_number_int,
                )
                await self.transaction.commit()
                await self.game_views.not_current_user_view(
                    user_id,
                    game,
                )
            except NoCellError:
                await self.log.no_cell_to_make_move(
                    game,
                    user_id,
                    cell_number_int,
                )
                await self.transaction.commit()
                await self.game_views.no_cell_view(user_id, game)
            except AlreadyFilledCellError:
                await self.log.already_filled_cell_to_make_move(
                    game,
                    user_id,
                    cell_number_int,
                )
                await self.transaction.commit()
                await self.game_views.already_filled_cell_error(
                    user_id,
                    game,
                )
            else:
                await self.log.user_move_maked(user_id, game, user_move)

                if game.is_completed():
                    await self.log.game_was_completed_by_user(user_id, game)

                await self.map_(tracking)

                if user_move.next_move_ai_id is not None:
                    await self.tasks.make_ai_move(
                        game.id, user_move.next_move_ai_id,
                    )

                await self.transaction.commit()
                await self.game_views.game_view(game)
