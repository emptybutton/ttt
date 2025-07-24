from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True)
class GameStartingQueuePush:
    was_location_dedublicated: bool


class GameStartingQueue(ABC):
    @abstractmethod
    async def push(
        self,
        location: UserLocation,
        /,
    ) -> GameStartingQueuePush: ...

    @abstractmethod
    async def push_many(
        self,
        locations: Sequence[UserLocation],
        /,
    ) -> None: ...

    @abstractmethod
    def __aiter__(
        self,
    ) -> AsyncIterator[tuple[UserLocation, UserLocation]]: ...
