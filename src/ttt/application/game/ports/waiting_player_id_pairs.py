from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class WaitingPlayerIdPairs(ABC):
    @abstractmethod
    async def push(self, id_: int, /) -> None: ...

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[tuple[int, int]]: ...
