from abc import ABC, abstractmethod

from ttt.entities.core.user.user import User


class CommonUserLog(ABC):
    @abstractmethod
    async def user_registered(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_double_registration(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_viewed(self, user_id: int, /) -> None: ...

    @abstractmethod
    async def user_removed_emoji(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def menu_viewed(self, user_id: int) -> None: ...

    @abstractmethod
    async def emoji_menu_viewed(self, user_id: int) -> None: ...
