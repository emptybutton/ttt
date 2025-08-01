from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.cell import AlreadyFilledCellError
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    NoCellError,
    NotCurrentPlayerError,
)
from ttt.entities.core.user.user import User
from ttt.entities.tools.assertion import not_none
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
    transaction: Transaction
    log: GameLog

    async def __call__(
        self,
        user_id: int,
        cell_number_int: int,
    ) -> None:
        async with self.transaction:
            game = await self.games.game_with_game_location(user_id)

            if game is None:
                await self.game_views.no_game_view(user_id)
                return

            locations = tuple(
                not_none(user.game_location)
                for user in (game.player1, game.player2)
                if isinstance(user, User)
            )
            (
                random,
                current_user_last_game_id,
                not_current_user_last_game_id,
            ) = await gather(
                self.randoms.random(),
                self.uuids.random_uuid(),
                self.uuids.random_uuid(),
            )

            try:
                tracking = Tracking()
                user_move = game.make_user_move(
                    user_id,
                    cell_number_int,
                    current_user_last_game_id,
                    not_current_user_last_game_id,
                    random,
                    tracking,
                )
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_make_move(
                    game,
                    user_id,
                    cell_number_int,
                )
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
                await self.game_views.no_cell_view(user_id, game)
            except AlreadyFilledCellError:
                await self.log.already_filled_cell_to_make_move(
                    game,
                    user_id,
                    cell_number_int,
                )
                await self.game_views.already_filled_cell_error(
                    user_id,
                    game,
                )
            else:
                await self.log.user_move_maked(user_id, game, user_move)

                if user_move.next_move_ai_id is not None:
                    await self.game_views.game_view_with_locations(
                        locations,
                        game,
                    )

                    (
                        free_cell_random,
                        ai_move_cell_number_int,
                        not_current_user_last_game_id,
                    ) = await gather(
                        self.randoms.random(),
                        self.ai_gateway.next_move_cell_number_int(
                            game,
                            user_move.next_move_ai_id,
                        ),
                        self.uuids.random_uuid(),
                    )
                    ai_move = game.make_ai_move(
                        user_move.next_move_ai_id,
                        ai_move_cell_number_int,
                        not_current_user_last_game_id,
                        free_cell_random,
                        tracking,
                    )

                    await self.log.ai_move_maked(
                        user_id,
                        game,
                        ai_move,
                    )

                if game.is_completed():
                    await self.log.game_completed(user_id, game)

                await self.map_(tracking)
                await self.game_views.game_view_with_locations(
                    locations,
                    game,
                )
