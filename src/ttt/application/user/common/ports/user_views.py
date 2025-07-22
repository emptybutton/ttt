from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation


class CommonUserViews(ABC):
    @abstractmethod
    async def view_of_user_with_id(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_registered_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_registered_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_registered_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def selected_emoji_removed_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
