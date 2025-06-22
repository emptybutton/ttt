from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass

from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True)
class WaitingLocationsPush:
    was_location_dedublicated: bool


class WaitingLocations(ABC):
    @abstractmethod
    async def push(
        self, location: PlayerLocation, /,
    ) -> WaitingLocationsPush: ...

    @abstractmethod
    async def push_many(
        self, location: Sequence[PlayerLocation], /,
    ) -> None: ...

    @abstractmethod
    def __aiter__(
        self,
    ) -> AsyncIterator[tuple[PlayerLocation, PlayerLocation]]: ...
