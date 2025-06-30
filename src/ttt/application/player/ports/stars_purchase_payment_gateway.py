from abc import ABC, abstractmethod
from collections.abc import AsyncIterable

from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase


class StarsPurchasePaymentGateway(ABC):
    @abstractmethod
    async def process_payment(
        self,
        purshase: StarsPurchase,
        location: PlayerLocation,
    ) -> None:
        ...

    @abstractmethod
    def paid_payment_stream(self) -> AsyncIterable[PaidStarsPurchasePayment]:
        ...
