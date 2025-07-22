from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation


class EmojiSelectionUserViews(ABC):
    @abstractmethod
    async def invalid_emoji_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_not_purchased_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_selected_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def wait_emoji_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
