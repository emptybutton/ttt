from abc import ABC, abstractmethod
from collections.abc import AsyncIterable

from ttt.application.player.common.dto.common import PaidStarsPurchasePayment


class PaidStarsPurchasePaymentInbox(ABC):
    @abstractmethod
    async def push(self, payment: PaidStarsPurchasePayment) -> None: ...

    @abstractmethod
    def stream(self) -> AsyncIterable[PaidStarsPurchasePayment]:
        ...
