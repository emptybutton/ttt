from abc import ABC, abstractmethod

from ttt.entities.core.user.user import User
from ttt.entities.text.emoji import Emoji


class EmojiSelectionUserLog(ABC):
    @abstractmethod
    async def user_selected_emoji(
        self,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_intends_to_select_emoji(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def emoji_not_purchased_to_select(
        self,
        user: User,
        emoji: Emoji,
        /,
    ) -> None: ...
