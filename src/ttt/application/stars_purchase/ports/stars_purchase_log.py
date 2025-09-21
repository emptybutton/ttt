from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.stars import Stars
from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase
from ttt.entities.core.user.user import User
from ttt.entities.finance.payment.success import PaymentSuccess


class StarsPurchaseLog(ABC):
    @abstractmethod
    async def stars_puchase_started(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_puchase_payment_started(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_purchase_payment_completion_started(
        self,
        purchase_id: UUID,
        success: PaymentSuccess,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_purchase_payment_completed(
        self,
        stars_purchase: StarsPurchase,
        success: PaymentSuccess,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_stars_purchase_payment_completion(
        self,
        stars_purchase: StarsPurchase,
        success: PaymentSuccess,
        /,
    ) -> None: ...

    @abstractmethod
    async def invalid_stars_for_stars_purchase(
        self,
        user: User,
        stars: Stars,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_stars_purchase_payment_start(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_stars_purchase_to_start_payment(
        self,
        purchase_id: UUID,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_stars_purchase_to_complete_payment(
        self,
        purchase_id: UUID,
        /,
    ) -> None: ...
