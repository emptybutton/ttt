from dataclasses import dataclass

from ttt.entities.tools.assertion import assert_


class NotOneCharEmojiError(Exception): ...


@dataclass(frozen=True)
class Emoji:
    char: str

    def __post_init__(self) -> None:
        assert_(len(self.char) == 1, else_=NotOneCharEmojiError)
