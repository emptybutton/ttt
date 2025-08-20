from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class GameStartingQueuePush:
    was_location_dedublicated: bool


class GameStartingQueue(ABC):
    @abstractmethod
    async def push(
        self,
        user_id: int,
        /,
    ) -> GameStartingQueuePush: ...

    @abstractmethod
    async def push_many(
        self,
        user_ids: Sequence[int],
        /,
    ) -> None: ...

    @abstractmethod
    def __aiter__(
        self,
    ) -> AsyncIterator[tuple[int, int]]: ...
