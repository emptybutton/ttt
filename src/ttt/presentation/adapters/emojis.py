from dataclasses import dataclass, field

from random_unicode_emoji import random_emoji

from ttt.application.common.ports.emojis import Emojis
from ttt.entities.telegram.emoji import Emoji
from ttt.entities.tools.assertion import not_none


@dataclass
class AllEmojis(Emojis):
    _avaiable_random_emojis: list[Emoji] = field(init=False)

    _selected_chars: set[str] = field(init=False, default_factory=set)

    async def random_emoji(self) -> Emoji:
        char: str | None = None
        was_char_selected = True

        while not was_char_selected:
            char, *_ = random_emoji()
            was_char_selected = char in self._selected_chars

        char = not_none(char)

        self._selected_chars.add(char)
        return Emoji(char)
