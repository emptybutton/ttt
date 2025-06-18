from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import chain
from typing import Any


class TrackingError(Exception): ...


@dataclass(frozen=True, unsafe_hash=False)
class Tracking[T = Any]:
    new: list[T] = field(default_factory=list)
    mutated: list[T] = field(default_factory=list)
    deleted: list[T] = field(default_factory=list)

    def __iter__(self) -> Iterator[T]:
        return chain(self.new, self.mutated, self.deleted)

    def __len__(self) -> int:
        return sum(map(len, (self.new, self.mutated, self.deleted)))

    def register_new(self, it: T) -> None:
        if it in self.new or it in self.mutated or it in self.deleted:
            raise TrackingError

        self.new.append(it)

    def register_mutated(self, it: T) -> None:
        if it in self.new or it in self.deleted:
            raise TrackingError

        if it not in self.mutated:
            self.mutated.append(it)

    def register_deleted(self, it: T) -> None:
        if it in self.new or it in self.mutated or it in self.deleted:
            raise TrackingError

        self.deleted.append(it)
