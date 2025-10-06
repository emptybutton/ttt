from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase


class StarsPurchases(ABC):
    @abstractmethod
    async def stars_purchase_with_id(
        self,
        id_: UUID,
        /,
    ) -> StarsPurchase | None: ...
