from abc import ABC, abstractmethod

from ttt.entities.core.user.user import User
from ttt.entities.text.emoji import Emoji


class EmojiPurchaseUserLog(ABC):
    @abstractmethod
    async def user_bought_emoji(
        self,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_intends_to_buy_emoji(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_already_purchased_to_buy(
        self,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...
