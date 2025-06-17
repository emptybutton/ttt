from dataclasses import dataclass

from ttt.application.common import (
    Map,
    PlayerViews,
    Transaction,
)
from ttt.entities.core import (
    create_player,
)
from ttt.entities.tools import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterUser:
    transaction: Transaction
    map: Map

    async def __call__(self, player_id: int) -> None:
        """
        :raises ttt.application.common.NotUniquePlayerIdError:
        """

        tracking = Tracking()

        create_player(player_id, tracking)

        async with self.transaction:
            await self.map(tracking)


@dataclass(frozen=True, unsafe_hash=False)
class ViewPlayer[PlayerViewWithIDT]:
    player_views: PlayerViews[PlayerViewWithIDT]
    transaction: Transaction

    async def __call__(self, player_id: int) -> PlayerViewWithIDT:
        async with self.transaction:
            return await self.player_views.view_of_player_with_id(player_id)
