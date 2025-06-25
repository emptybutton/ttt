from dataclasses import dataclass

from ttt.entities.tools.assertion import assert_


class InvalidEmojiError(Exception): ...


@dataclass(frozen=True)
class Emoji:
    str_: str

    def __post_init__(self) -> None:
        assert_(len(self.str_) == 1, InvalidEmojiError)
