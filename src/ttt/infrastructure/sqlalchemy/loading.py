from dataclasses import dataclass
from typing import Any, Protocol, overload

from sqlalchemy.ext.asyncio import AsyncSession

from ttt.infrastructure.sqlalchemy.sequence_map import SequenceMap


class Loadable[T](Protocol):
    async def __entity__(self, loading: "Loading") -> T: ...


@dataclass(frozen=True, unsafe_hash=True)
class Loading:
    session: AsyncSession
    _map: SequenceMap[Any, Loadable[Any]]

    @overload
    async def load[T](self, value: None) -> None: ...
    @overload
    async def load[T](self, value: Loadable[T]) -> T: ...
    async def load[T](self, value: Loadable[T] | None) -> T | None:
        if value is None:
            return None

        entity = await value.__entity__(self)
        self._map[entity] = value

        return entity

    def loadable[T](self, entity: T) -> Loadable[T] | None:
        return self._map.get(entity)
