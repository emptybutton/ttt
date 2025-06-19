from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from ttt.entities.core.player.location import JustLocation


class WaitingLocations(ABC):
    @abstractmethod
    async def push(self, location: JustLocation, /) -> None: ...

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[tuple[JustLocation, JustLocation]]: ...
