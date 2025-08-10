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
