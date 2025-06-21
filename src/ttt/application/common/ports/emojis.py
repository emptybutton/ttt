from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from ttt.entities.text.emoji import Emoji


class Emojis(AbstractAsyncContextManager["Emojis"], ABC):
    @abstractmethod
    async def random_emoji(self) -> Emoji: ...
