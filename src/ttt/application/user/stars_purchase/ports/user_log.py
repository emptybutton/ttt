from abc import ABC, abstractmethod

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


class StarsPurchaseUserLog(ABC):
    @abstractmethod
    async def user_intends_to_buy_stars(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_started_stars_puchase(
        self, location: UserLocation, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def user_started_stars_puchase_payment(
        self, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def stars_purshase_payment_completion_started(
        self, payment: PaidStarsPurchasePayment, /,
    ) -> None: ...

    @abstractmethod
    async def stars_purshase_payment_completed(
        self, user: User, payment: PaidStarsPurchasePayment, /,
    ) -> None: ...
