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
    async def user_authorized_as_admin(
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
    async def not_admin_to_relinquish_admin_right(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_relinquished_admin_rights(self, user: User, /) -> None: ...

    @abstractmethod
    async def not_authorized_as_admin_via_admin_token_to_authorize_other_user_as_admin(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None: ...

    @abstractmethod
    async def other_user_already_admin_to_authorize_other_user_as_admin(
        self, user: User, other_user: User | None, /,
    ) -> None: ...

    @abstractmethod
    async def user_authorized_other_user_as_admin(
        self, user: User, other_user: User | None, /,
    ) -> None: ...

    @abstractmethod
    async def not_authorized_as_admin_via_admin_token_to_deauthorize_other_user_as_admin(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None: ...

    @abstractmethod
    async def other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None: ...

    @abstractmethod
    async def user_deauthorized_other_user_as_admin(
        self, user: User, other_user: User | None, /,
    ) -> None: ...
