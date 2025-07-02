from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.player.common.ports.player_fsm import PlayerFsm
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.application.player.common.ports.players import Players
from ttt.application.player.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import (
    InvalidStarsForStarsPurchaseError,
    StarsPurchase,
)
from ttt.entities.core.stars import Stars
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchase:
    fsm: PlayerFsm
    transaction: Transaction
    players: Players
    uuids: UUIDs
    clock: Clock
    player_views: PlayerViews
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map

    async def __call__(self, location: PlayerLocation, stars: Stars) -> None:
        async with self.transaction:
            player, purchase_id = await gather(
                self.players.player_with_id(location.player_id),
                self.uuids.random_uuid(),
            )

            if player is None:
                await self.player_views.render_player_is_not_registered_view(
                    location,
                )
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                player.start_stars_purchase(
                    purchase_id,
                    location.chat_id,
                    stars,
                    tracking,
                )
            except InvalidStarsForStarsPurchaseError:
                await self.fsm.set(None)
                await (
                    self.player_views
                    .render_invalid_stars_for_stars_purchase_view(location)
                )
                return

            await self.map_(tracking)
            await self.fsm.set(None)
            await gather(*[
                self.payment_gateway.send_invoice(it, location)
                for it in tracking.new
                if isinstance(it, StarsPurchase)
            ])
