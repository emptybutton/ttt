from abc import ABC, abstractmethod
from collections.abc import AsyncIterable

from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.player.location import PlayerLocation


class StarsPurchasePaymentGateway(ABC):
    @abstractmethod
    async def start_payment(self, location: PlayerLocation) -> None:
        ...

    @abstractmethod
    def paid_payment_stream(self) -> AsyncIterable[PaidStarsPurchasePayment]:
        ...
