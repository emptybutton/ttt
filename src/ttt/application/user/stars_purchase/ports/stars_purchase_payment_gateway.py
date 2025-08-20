from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from uuid import UUID

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.user.stars_purchase import StarsPurchase


class StarsPurchasePaymentGateway(ABC):
    @abstractmethod
    async def send_invoice(self, purchase: StarsPurchase) -> None: ...

    @abstractmethod
    async def start_payment(self, payment_id: UUID) -> None: ...

    @abstractmethod
    async def stop_payment_due_to_dublicate(self, payment_id: UUID) -> None: ...

    @abstractmethod
    async def stop_payment_due_to_error(self, payment_id: UUID) -> None: ...

    @abstractmethod
    def paid_payment_stream(
        self,
    ) -> AsyncIterable[PaidStarsPurchasePayment]: ...
