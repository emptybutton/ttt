from abc import ABC, abstractmethod

from ttt.entities.core.user.user import User


class CommonUserViews(ABC):
    @abstractmethod
    async def view_of_user_with_id(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def view_of_user_emojis_with_id(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_registered_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_menu_view(self, user_id: int, /) -> None: ...

    @abstractmethod
    async def user_got_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_admin_to_get_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def admin_token_mismatch_to_get_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_admin_to_relinquish_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_relinquished_admin_rights_view(self, user: User, /) -> None:
        ...

    @abstractmethod
    async def user_admin_view(self, user_id: int, /) -> None:
        ...
