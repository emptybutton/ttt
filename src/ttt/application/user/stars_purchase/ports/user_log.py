from abc import ABC, abstractmethod
from uuid import UUID

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.user import User


class StarsPurchaseUserLog(ABC):
    @abstractmethod
    async def user_intends_to_buy_stars(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_started_stars_puchase(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_started_stars_puchase_payment(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_purchase_payment_completion_started(
        self,
        payment: PaidStarsPurchasePayment,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_purchase_payment_completed(
        self,
        user: User,
        payment: PaidStarsPurchasePayment,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_stars_purchase_payment_completion(
        self,
        user: User,
        paid_payment: PaidStarsPurchasePayment,
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
        user: User,
        purchase_id: UUID,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_purchase_to_start_stars_purchase_payment(
        self,
        user: User,
        purchase_id: UUID,
        /,
    ) -> None: ...
