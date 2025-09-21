from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.finance.payment.success import PaymentSuccess


class StarsPurchaseTasks(ABC):
    @abstractmethod
    async def complete_stars_purchase_payment(
        self,
        purchase_id: UUID,
        success: PaymentSuccess,
        /,
    ) -> None: ...
