from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class Combinations[V](Iterator[tuple[V, V]]):
    _values: list[V]

    _index1: int = field(init=False, default=0)
    _index2: int = field(init=False, default=0)

    def __next__(self) -> tuple[V, V]:
        self._index2 += 1

        if self._index2 >= len(self._values):
            self._index1 += 1
            self._index2 = self._index1 + 1

            if self._index1 >= len(self._values) - 1:
                raise StopIteration

        return self._values[self._index1], self._values[self._index2]

    def cut(self) -> None:
        del self._values[self._index2]
        del self._values[self._index1]

        self._index2 = self._index1
