from collections.abc import AsyncIterable
from dataclasses import dataclass

from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.application.player.ports.paid_stars_purchase_payment_inbox import (
    PaidStarsPurchasePaymentInbox,
)
from ttt.infrastructure.nats.paid_stars_purchase_payment_inbox import (
    InNatsPaidStarsPurchasePaymentInbox as OriginalInNatsPaidStarsPurchasePaymentInbox,  # noqa: E501
)


@dataclass(frozen=True)
class InNatsPaidStarsPurchasePaymentInbox(PaidStarsPurchasePaymentInbox):
    _inbox: OriginalInNatsPaidStarsPurchasePaymentInbox

    async def push(self, payment: PaidStarsPurchasePayment) -> None:
        await self._inbox.push(payment)

    async def stream(self) -> AsyncIterable[PaidStarsPurchasePayment]:
        async for payment in self._inbox:
            yield payment
