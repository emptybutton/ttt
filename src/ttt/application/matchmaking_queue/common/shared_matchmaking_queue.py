from abc import ABC
from collections.abc import Awaitable

from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    MatchmakingQueue,
)


class SharedMatchmakingQueue(ABC, Awaitable[MatchmakingQueue]): ...
