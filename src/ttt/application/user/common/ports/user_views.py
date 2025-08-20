from abc import ABC, abstractmethod


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
