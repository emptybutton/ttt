from dataclasses import dataclass
from typing import Any, Protocol, overload

from ttt.infrastructure.sequence_map import SequenceMap


class Loadable[T](Protocol):
    def __entity__(self, loading: "Loading", /) -> T: ...


@dataclass(frozen=True, unsafe_hash=True)
class Loading:
    _map: SequenceMap[Any, Loadable[Any]]

    @overload
    def load[T](self, value: None) -> None: ...
    @overload
    def load[T](self, value: Loadable[T]) -> T: ...
    def load[T](self, value: Loadable[T] | None) -> T | None:
        if value is None:
            return None

        entity = value.__entity__(self)
        self._map[entity] = value

        return entity

    def loadable[T](self, entity: T) -> Loadable[T] | None:
        return self._map.get(entity)
