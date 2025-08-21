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
    async def user_got_admin_rights(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_admin_to_get_admin_rights(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def admin_token_mismatch_to_get_admin_rights(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_admin_to_relinquish_admin_rights(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_relinquished_admin_rights(self, user: User, /) -> None: ...
