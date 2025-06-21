from dataclasses import dataclass, field
from types import TracebackType

from random_unicode_emoji.random_unicode_emoji import random_emoji

from ttt.application.common.ports.emojis import Emojis
from ttt.entities.text.emoji import Emoji


@dataclass
class AllEmojis(Emojis):
    _selected_emojis: set[Emoji] = field(init=False, default_factory=set)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._selected_emojis = set()

    async def random_emoji(self) -> Emoji:
        char, *_ = random_emoji()
        emoji = Emoji(char)

        while emoji not in self._selected_emojis:
            char, *_ = random_emoji()
            emoji = Emoji(char)

        self._selected_emojis.add(emoji)
        return emoji
