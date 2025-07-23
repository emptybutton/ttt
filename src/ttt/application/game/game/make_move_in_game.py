from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.cell import AlreadyFilledCellError
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    NoCellError,
    NotCurrentPlayerError,
)
from ttt.entities.core.user.location import UserLocation
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
        location: UserLocation,
        cell_number_int: int,
    ) -> None:
        async with self.transaction:
            game = await self.games.game_with_game_location(location.user_id)

            if game is None:
                await self.game_views.no_game_view(location)
                return

            locations = tuple(
                not_none(user.game_location)
                for user in (game.player1, game.player2)
                if isinstance(user, User)
            )
            game_result_id, random = await gather(
                self.uuids.random_uuid(),
                self.randoms.random(),
            )

            try:
                tracking = Tracking()
                user_move = game.make_user_move(
                    location.user_id,
                    cell_number_int,
                    game_result_id,
                    random,
                    tracking,
                )
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_make_move(
                    game,
                    location,
                    cell_number_int,
                )
                await self.game_views.game_already_complteted_view(
                    location,
                    game,
                )
            except NotCurrentPlayerError:
                await self.log.not_current_player_to_make_move(
                    game,
                    location,
                    cell_number_int,
                )
                await self.game_views.not_current_user_view(
                    location,
                    game,
                )
            except NoCellError:
                await self.log.no_cell_to_make_move(
                    game,
                    location,
                    cell_number_int,
                )
                await self.game_views.no_cell_view(location, game)
            except AlreadyFilledCellError:
                await self.log.already_filled_cell_to_make_move(
                    game,
                    location,
                    cell_number_int,
                )
                await self.game_views.already_filled_cell_error(
                    location,
                    game,
                )
            else:
                await self.log.user_move_maked(location, game, user_move)

                if user_move.next_move_ai_id is not None:
                    await self.game_views.game_view_with_locations(
                        locations,
                        game,
                    )

                    game_result_id = await self.uuids.random_uuid()
                    free_cell_random = await self.randoms.random()
                    ai_move_cell_number_int = (
                        await self.ai_gateway.next_move_cell_number_int(
                            game,
                            user_move.next_move_ai_id,
                        )
                    )
                    ai_move = game.make_ai_move(
                        user_move.next_move_ai_id,
                        ai_move_cell_number_int,
                        game_result_id,
                        free_cell_random,
                        tracking,
                    )

                    await self.log.ai_move_maked(
                        location,
                        game,
                        ai_move,
                    )

                if game.is_completed():
                    await self.log.game_completed(location, game)

                await self.map_(tracking)
                await self.game_views.game_view_with_locations(
                    locations,
                    game,
                )
