from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.user.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.application.user.common.ports.users import Users
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.entities.core.user.user import NoPurchaseError
from ttt.entities.finance.payment.payment import PaymentIsAlreadyBeingMadeError
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchasePayment:
    transaction: Transaction
    uuids: UUIDs
    clock: Clock
    users: Users
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map
    log: StarsPurchaseUserLog

    async def __call__(self, user_id: int, purchase_id: UUID) -> None:
        async with self.transaction:
            user, payment_id, current_datetime = await gather(
                self.users.user_with_id(user_id),
                self.uuids.random_uuid(),
                self.clock.current_datetime(),
            )
            user = not_none(user)

            tracking = Tracking()
            try:
                user.start_stars_purchase_payment(
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
                await self.log.user_started_stars_puchase_payment(user)
                await self.map_(tracking)
                await self.payment_gateway.start_payment(payment_id)
