from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.ports.games import Games
from ttt.entities.core.game.game import GameResult
from ttt.entities.math.vector import Vector
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class MakeMoveInGame:
    map_: Map
    games: Games
    players: Players
    uuids: UUIDs
    transaction: Transaction

    async def __call__(
        self,
        player_id: int,
        cell_position: Vector,
    ) -> GameResult | None:
        """
        :raises ttt.application.common.ports.players.NoPlayerError:
        :raises ttt.application.game.ports.games.NoGameError:
        :raises ttt.entities.core.game.game.CompletedGameError:
        :raises ttt.entities.core.game.game.NotCurrentPlayerError:
        :raises ttt.entities.core.game.game.NoCellError:
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        player = await self.players.player_with_id(player_id)
        game = await self.games.game_with_id(player.current_game_id)
        game_result_id = await self.uuids.random_uuid()

        tracking = Tracking()
        game_result = game.make_move(
            player.id, cell_position, game_result_id, tracking,
        )

        async with self.transaction:
            await self.map_(tracking)

        return game_result
