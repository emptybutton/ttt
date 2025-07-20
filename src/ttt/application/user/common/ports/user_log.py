from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User
from ttt.entities.text.emoji import Emoji


class CommonUserLog(ABC):
    @abstractmethod
    async def user_registered(
        self, location: UserLocation, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def user_double_registration(
        self, location: UserLocation, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def user_viewed(self, location: UserLocation, /) -> None: ...

    @abstractmethod
    async def user_removed_emoji(
        self, location: UserLocation, user: User, /,
    ) -> None: ...
