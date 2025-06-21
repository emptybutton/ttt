from dataclasses import dataclass


@dataclass(frozen=True)
class Emoji:
    char: str
