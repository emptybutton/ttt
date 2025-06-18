from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass


@dataclass(frozen=True, unsafe_hash=False)
class SequenceMap[K, V](MutableMapping[K, V]):
    _pairs: list[tuple[K, V]]

    def __iter__(self) -> Iterator[K]:
        return (key for key, _ in self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)

    def __getitem__(self, key: K) -> V:
        for stored_key, value in self._pairs:
            if stored_key == key:
                return value

        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        index = self._index(key)

        if index is not None:
            self._pairs[index] = (key, value)
            return

        index = len(self._pairs)
        self._pairs[index] = (key, value)

    def __delitem__(self, key: K, /) -> None:
        index = self._index(key)

        if index is None:
            raise KeyError(key)

        del self._pairs[index]

    def _index(self, key: K) -> int | None:
        for index in range(len(self._pairs)):
            stored_key, _ = self._pairs[index]

            if stored_key == key:
                return index

        return None
