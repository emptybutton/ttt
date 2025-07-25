from abc import ABC, abstractmethod

from ttt.entities.core.stars import Stars


class EmojiPurchaseUserViews(ABC):
    @abstractmethod
    async def wait_emoji_to_buy_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_enough_stars_to_buy_emoji_view(
        self,
        user_id: int,
        stars_to_become_enough: Stars,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_already_purchased_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_was_purchased_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def invalid_emoji_to_buy_view(
        self,
        user_id: int,
        /,
    ) -> None: ...
