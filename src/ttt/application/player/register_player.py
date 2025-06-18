from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.entities.core.player import create_player
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterPlayer:
    transaction: Transaction
    map: Map

    async def __call__(self, player_id: int) -> None:
        """
        :raises ttt.application.common.ports.map.NotUniquePlayerIdError:
        """

        tracking = Tracking()

        create_player(player_id, tracking)

        async with self.transaction:
            await self.map(tracking)
