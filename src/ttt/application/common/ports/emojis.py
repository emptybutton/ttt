from abc import ABC, abstractmethod

from ttt.entities.telegram.emoji import Emoji


class Emojis(ABC):
    @abstractmethod
    async def random_emoji(self) -> Emoji: ...
