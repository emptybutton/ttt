from abc import ABC, abstractmethod

from ttt.entities.core.stars import Stars
from ttt.entities.core.user.location import UserLocation


class EmojiPurchaseUserViews(ABC):
    @abstractmethod
    async def wait_emoji_to_buy_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_enough_stars_to_buy_emoji_view(
        self,
        location: UserLocation,
        stars_to_become_enough: Stars,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_already_purchased_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_was_purchased_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def invalid_emoji_to_buy_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
