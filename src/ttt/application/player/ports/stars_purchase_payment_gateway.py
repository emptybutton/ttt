from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.entities.finance.payment.success import PaymentSuccess


@dataclass(frozen=True)
class PaidStarsPurchasePayment:
    purshase_id: UUID
    location: PlayerLocation
    success: PaymentSuccess


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
