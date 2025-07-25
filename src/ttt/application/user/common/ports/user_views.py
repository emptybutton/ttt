from abc import ABC, abstractmethod


class CommonUserViews(ABC):
    @abstractmethod
    async def view_of_user_with_id(
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
    async def user_already_registered_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_registered_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def selected_emoji_removed_view(
        self,
        user_id: int,
        /,
    ) -> None: ...
