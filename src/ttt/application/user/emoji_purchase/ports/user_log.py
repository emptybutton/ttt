from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User
from ttt.entities.text.emoji import Emoji


class EmojiPurchaseUserLog(ABC):
    @abstractmethod
    async def user_bought_emoji(
        self,
        location: UserLocation,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_intends_to_buy_emoji(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_already_purchased_to_buy(
        self,
        user: User,
        location: UserLocation,
        emoji: Emoji,
        /,
    ) -> None: ...
