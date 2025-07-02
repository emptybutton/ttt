from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.player.ports.players import Players
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.player import NoPurchaseError
from ttt.entities.finance.payment.payment import PaymentIsAlreadyBeingMadeError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchasePayment:
    transaction: Transaction
    uuids: UUIDs
    clock: Clock
    players: Players
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map

    async def __call__(self, player_id: int, purchase_id: UUID) -> None:
        async with self.transaction:
            player, payment_id, current_datetime = await gather(
                self.players.player_with_id(player_id),
                self.uuids.random_uuid(),
                self.clock.current_datetime(),
            )

            tracking = Tracking()
            try:
                player.start_stars_purchase_payment(
                    purchase_id, payment_id, current_datetime, tracking,
                )
            except PaymentIsAlreadyBeingMadeError:
                await self.payment_gateway.stop_payment_due_to_dublicate(
                    payment_id,
                )
            except NoPurchaseError:
                await self.payment_gateway.stop_payment_due_to_error(
                    payment_id,
                )
            else:
                await self.map_(tracking)
                await self.payment_gateway.start_payment(payment_id)
