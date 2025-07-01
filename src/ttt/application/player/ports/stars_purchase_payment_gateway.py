from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from uuid import UUID

from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase


class StarsPurchasePaymentGateway(ABC):
    @abstractmethod
    async def send_invoice(
        self,
        purshase: StarsPurchase,
        location: PlayerLocation,
    ) -> None: ...

    @abstractmethod
    async def start_payment(self, payment_id: UUID) -> None: ...

    @abstractmethod
    async def stop_payment_due_to_dublicate(self, payment_id: UUID) -> None:
        ...

    @abstractmethod
    async def stop_payment_due_to_error(self, payment_id: UUID) -> None: ...

    @abstractmethod
    def paid_payment_stream(self) -> AsyncIterable[PaidStarsPurchasePayment]:
        ...
