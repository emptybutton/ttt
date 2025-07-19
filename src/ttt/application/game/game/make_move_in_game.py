from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
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

    async def __call__(
        self,
        location: UserLocation,
        cell_number_int: int,
    ) -> None:
        async with self.transaction:
            game = await self.games.game_with_game_location(location.user_id)

            if game is None:
                await self.game_views.render_no_game_view(location)
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
                move = game.make_move(
                    location.user_id,
                    cell_number_int,
                    game_result_id,
                    random,
                    tracking,
                )
            except AlreadyCompletedGameError:
                await self.game_views.render_game_already_complteted_view(
                    location, game,
                )
            except NotCurrentPlayerError:
                await self.game_views.render_not_current_user_view(
                    location, game,
                )
            except NoCellError:
                await self.game_views.render_no_cell_view(location, game)
            except AlreadyFilledCellError:
                await self.game_views.render_already_filled_cell_error(
                    location, game,
                )
            else:
                if move.next_move_ai_id is not None:
                    await self.game_views.render_game_view_with_locations(
                        locations, game,
                    )

                    game_result_id = await self.uuids.random_uuid()
                    free_cell_random = await self.randoms.random()
                    ai_move_cell_number_int = (
                        await self.ai_gateway.next_move_cell_number_int(
                            game,
                            move.next_move_ai_id,
                        )
                    )
                    game.make_ai_move(
                        move.next_move_ai_id,
                        ai_move_cell_number_int,
                        game_result_id,
                        free_cell_random,
                        tracking,
                    )

                    await self.map_(tracking)
                    await self.game_views.render_game_view_with_locations(
                        locations, game,
                    )
                else:
                    await self.map_(tracking)
                    await self.game_views.render_game_view_with_locations(
                        locations, game,
                    )
