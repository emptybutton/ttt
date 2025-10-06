from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.retry import Retry
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.stars_purchase.ports.stars_purchase_log import (
    StarsPurchaseLog,
)
from ttt.application.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.application.stars_purchase.ports.stars_purchases import StarsPurchases
from ttt.entities.finance.payment.payment import PaymentIsAlreadyBeingMadeError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurchasePayment:
    transaction: SerializableTransaction
    uuids: UUIDs
    clock: Clock
    stars_purchases: StarsPurchases
    payment_gateway: StarsPurchasePaymentGateway
    map_: Map
    log: StarsPurchaseLog
    retry: Retry

    async def __call__(self, purchase_id: UUID) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            stars_purchase, payment_id, current_datetime = await gather(
                self.stars_purchases.stars_purchase_with_id(purchase_id),
                self.uuids.random_uuid(),
                self.clock.current_datetime(),
            )

            if stars_purchase is None:
                await self.log.no_stars_purchase_to_start_payment(purchase_id)
                await self.payment_gateway.stop_payment_due_to_error(payment_id)
                return

            try:
                tracking = Tracking()
                stars_purchase.start_payment(
                    payment_id,
                    current_datetime,
                    tracking,
                )
            except PaymentIsAlreadyBeingMadeError:
                await self.log.double_stars_purchase_payment_start(
                    stars_purchase,
                )
                await self.transaction.commit()

                if self.retry:
                    await self.payment_gateway.start_payment(payment_id)
                else:
                    await self.payment_gateway.stop_payment_due_to_dublicate(
                        payment_id,
                    )
            else:
                await self.log.stars_puchase_payment_started(
                    stars_purchase,
                )
                await self.map_(tracking)
                await self.transaction.commit()
                await self.payment_gateway.start_payment(payment_id)
