from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.ports.game_views import GameViews
from ttt.application.game.ports.games import Games
from ttt.entities.core.game.game import GameResult
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.math.vector import Vector
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class MakeMoveInGame:
    map_: Map
    games: Games
    game_views: GameViews
    players: Players
    uuids: UUIDs
    transaction: Transaction

    async def __call__(
        self,
        location: PlayerLocation,
        cell_position: Vector,
    ) -> GameResult | None:
        """
        :raises ttt.application.common.ports.players.NoPlayerWithIDError:
        :raises ttt.application.game.ports.games.NoGameError:
        :raises ttt.entities.core.game.game.CompletedGameError:
        :raises ttt.entities.core.game.game.NotCurrentPlayerError:
        :raises ttt.entities.core.game.game.NoCellError:
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        async with self.transaction:
            player = await self.players.player_with_id(location.player_id)
            game = await self.games.game_with_id(
                None
                if player.game_location is None
                else player.game_location.game_id,
            )
            game_result_id = await self.uuids.random_uuid()

            tracking = Tracking()
            result = game.make_move(
                player.id, cell_position, game_result_id, tracking,
            )

            locations = tuple(
                not_none(player.game_location)
                for player in (game.player1, game.player2)
            )
            await self.map_(tracking)
            await self.game_views.render_game_view_with_locations(
                locations, game,
            )
            return result
