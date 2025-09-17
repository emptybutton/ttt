from abc import ABC
from collections.abc import Awaitable

from ttt.entities.core.matchmaking.matchmaking import (
    Matchmaking,
)


class SharedMatchmaking(ABC, Awaitable[Matchmaking]): ...
