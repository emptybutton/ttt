from abc import ABC, abstractmethod

from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase


class StarsPurchaseViews(ABC):
    @abstractmethod
    async def invalid_stars_for_stars_purchase_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_purchase_will_be_completed_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def completed_stars_purchase_view(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None: ...
