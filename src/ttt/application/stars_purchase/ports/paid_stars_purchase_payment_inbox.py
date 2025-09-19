from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from ttt.application.stars_purchase.dto.common import PaidStarsPurchasePayment


class PaidStarsPurchasePaymentInbox(ABC):
    @abstractmethod
    async def push(self, payment: PaidStarsPurchasePayment) -> None: ...

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[PaidStarsPurchasePayment]: ...
