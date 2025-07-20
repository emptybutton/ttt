from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


class EmojiPurchaseUserLog(ABC):
    @abstractmethod
    async def user_bought_emoji(
        self, location: UserLocation, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def user_intends_to_buy_emoji(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
