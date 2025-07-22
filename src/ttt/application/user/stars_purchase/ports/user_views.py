from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


class StarsPurchaseUserViews(ABC):
    @abstractmethod
    async def wait_stars_to_start_stars_purshase_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def invalid_stars_for_stars_purchase_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def stars_purchase_will_be_completed_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def completed_stars_purshase_view(
        self,
        user: User,
        purshase_id: UUID,
        location: UserLocation,
        /,
    ) -> None: ...
