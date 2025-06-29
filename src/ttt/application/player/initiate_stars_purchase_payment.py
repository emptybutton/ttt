from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.player.ports.player_fsm import PlayerFsm
from ttt.application.player.ports.player_views import PlayerViews
from ttt.application.player.ports.players import Players
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.entities.core.stars import NonExchangeableRublesForStarsError
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class InitiateStarsPurchasePayment:
    fsm: PlayerFsm
    transaction: Transaction
    players: Players
    uuids: UUIDs
    clock: Clock
    player_views: PlayerViews
    payment_gateway: StarsPurchasePaymentGateway

    async def __call__(
        self, location: PlayerLocation, rubles: Rubles,
    ) -> None:
        async with self.transaction:
            player, purchase_id, payment_id, current_datetime = await gather(
                self.players.player_with_id(location.player_id),
                self.uuids.random_uuid(),
                self.uuids.random_uuid(),
                self.clock.current_datetime(),
            )

            tracking = Tracking()
            try:
                player.initiate_stars_purchase_payment(
                    purchase_id,
                    location.chat_id,
                    payment_id,
                    rubles,
                    current_datetime,
                    tracking,
                )
            except NonExchangeableRublesForStarsError:
                await self.fsm.set(None)
                await (
                    self.player_views
                    .render_non_exchangeable_rubles_for_stars_view(location)
                )
                return

            await self.fsm.set(None)
            await gather(*[
                self.payment_gateway.process_payment(it, location)
                for it in tracking.new
                if isinstance(it, StarsPurchase)
            ])
