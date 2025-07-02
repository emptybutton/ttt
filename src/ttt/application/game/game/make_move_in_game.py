from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.application.player.common.ports.players import Players
from ttt.entities.core.game.cell import AlreadyFilledCellError
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    NoCellError,
    NotCurrentPlayerError,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class MakeMoveInGame:
    map_: Map
    games: Games
    game_views: GameViews
    players: Players
    uuids: UUIDs
    randoms: Randoms
    transaction: Transaction

    async def __call__(
        self,
        location: PlayerLocation,
        cell_number_int: int,
    ) -> None:
        async with self.transaction:
            game = await self.games.game_with_game_location(location.player_id)

            if game is None:
                await self.game_views.render_no_game_view(location)
                return

            locations = tuple(
                not_none(player.game_location)
                for player in (game.player1, game.player2)
            )
            game_result_id, random = await gather(
                self.uuids.random_uuid(),
                self.randoms.random(),
            )

            try:
                tracking = Tracking()
                game.make_move(
                    location.player_id,
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
                await self.game_views.render_not_current_player_view(
                    location, game,
                )
            except NoCellError:
                await self.game_views.render_no_cell_view(location, game)
            except AlreadyFilledCellError:
                await self.game_views.render_already_filled_cell_error(
                    location, game,
                )
            else:
                await self.map_(tracking)
                await self.game_views.render_game_view_with_locations(
                    locations, game,
                )
