from collections.abc import AsyncIterator
from dataclasses import dataclass

from ttt.application.stars_purchase.dto.common import PaidStarsPurchasePayment
from ttt.application.stars_purchase.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
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

    async def __aiter__(self) -> AsyncIterator[PaidStarsPurchasePayment]:
        async for payment in self._inbox:
            yield payment
