from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


class CommonUserLog(ABC):
    @abstractmethod
    async def user_registered(
        self,
        location: UserLocation,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_double_registration(
        self,
        location: UserLocation,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_viewed(self, location: UserLocation, /) -> None: ...

    @abstractmethod
    async def user_removed_emoji(
        self,
        location: UserLocation,
        user: User,
        /,
    ) -> None: ...
