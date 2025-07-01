from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.player.ports.players import Players
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class ApproveStarsPurchaseInvoce:
    transaction: Transaction
    players: Players
    uuids: UUIDs
    clock: Clock
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map

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
            player.initiate_stars_purchase_payment(
                purchase_id,
                location.chat_id,
                payment_id,
                rubles,
                current_datetime,
                tracking,
            )

            await self.map_(tracking)
            await self.payment_gateway.start_payment(location)
