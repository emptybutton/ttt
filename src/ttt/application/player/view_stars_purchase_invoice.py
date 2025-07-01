from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.player.ports.player_fsm import PlayerFsm
from ttt.application.player.ports.player_views import PlayerViews
from ttt.application.player.ports.players import Players
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.stars import (
    NonExchangeableRublesForStarsError,
    purchased_stars_for_rubles,
)
from ttt.entities.finance.rubles import Rubles


@dataclass(frozen=True, unsafe_hash=False)
class ViewStarsPurchaseInvoice:
    fsm: PlayerFsm
    transaction: Transaction
    players: Players
    uuids: UUIDs
    clock: Clock
    player_views: PlayerViews
    map_: Map

    async def __call__(self, location: PlayerLocation, rubles: Rubles) -> None:
        try:
            stars = purchased_stars_for_rubles(rubles)
        except NonExchangeableRublesForStarsError:
            await (
                self.player_views.render_non_exchangeable_rubles_for_stars_view(
                    location,
                )
            )
            return

        await self.player_views.render_stars_purchase_invoice_view(
            location, stars, rubles,
        )
