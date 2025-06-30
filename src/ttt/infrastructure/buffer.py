from asyncio import Event
from collections import deque
from collections.abc import AsyncIterator
from dataclasses import dataclass, field


@dataclass(frozen=True, unsafe_hash=False)
class Buffer[ValueT]:
    _values: deque[ValueT] = field(default_factory=deque)
    _has_values: Event = field(default_factory=Event, init=False)

    def __post_init__(self) -> None:
        if self._values:
            self._has_values.set()

    def __len__(self) -> int:
        return len(self._values)

    def add(self, value: ValueT) -> None:
        self._values.append(value)
        self._has_values.set()

    async def stream(self) -> AsyncIterator[ValueT]:
        while True:
            await self._has_values.wait()
            yield self._values.popleft()

            if not self._values:
                self._has_values.clear()
