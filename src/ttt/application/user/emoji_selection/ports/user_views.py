from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation


class EmojiSelectionUserViews(ABC):
    @abstractmethod
    async def render_invalid_emoji_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_not_purchased_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_selected_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_wait_emoji_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
