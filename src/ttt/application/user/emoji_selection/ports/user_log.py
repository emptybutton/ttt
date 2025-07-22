from abc import ABC, abstractmethod

from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User
from ttt.entities.text.emoji import Emoji


class EmojiSelectionUserLog(ABC):
    @abstractmethod
    async def user_selected_emoji(
        self,
        location: UserLocation,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_intends_to_select_emoji(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_not_purchased_to_select(
        self,
        location: UserLocation,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...
