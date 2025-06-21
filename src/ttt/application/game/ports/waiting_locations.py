from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence

from ttt.entities.core.player.location import PlayerLocation


class WaitingLocations(ABC):
    @abstractmethod
    async def push(self, location: PlayerLocation, /) -> None: ...

    @abstractmethod
    async def push_many(
        self, location: Sequence[PlayerLocation], /,
    ) -> None: ...

    @abstractmethod
    def __aiter__(
        self,
    ) -> AsyncIterator[tuple[PlayerLocation, PlayerLocation]]: ...
