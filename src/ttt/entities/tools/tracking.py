from collections.abc import Iterator
from dataclasses import dataclass, field
from itertools import chain
from typing import Any


class TrackingError(Exception): ...


@dataclass(frozen=True, unsafe_hash=False)
class Tracking[T = Any]:
    new: list[T] = field(default_factory=list)
    mutated: list[T] = field(default_factory=list)
    unused: list[T] = field(default_factory=list)

    def __iter__(self) -> Iterator[T]:
        return chain(self.new, self.mutated, self.unused)

    def __len__(self) -> int:
        return sum(map(len, (self.new, self.mutated, self.unused)))

    def register_new(self, it: T) -> None:
        if it in self.new or it in self.mutated or it in self.unused:
            raise TrackingError

        self.new.append(it)

    def register_mutated(self, it: T) -> None:
        if it in self.new or it in self.unused:
            return

        if it not in self.mutated:
            self.mutated.append(it)

    def register_unused(self, it: T) -> None:
        if it in self.new:
            self.new.remove(it)

        if it in self.mutated:
            self.mutated.remove(it)
            return

        if it in self.unused:
            raise TrackingError

        self.unused.append(it)
