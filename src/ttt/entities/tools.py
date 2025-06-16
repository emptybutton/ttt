from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import chain
from typing import Any, Literal, NoReturn, overload


def not_none[ValueT](
    value: ValueT | None,
    else_: Exception | type[Exception] = ValueError,
) -> ValueT:
    if value is not None:
        return value

    raise else_


@overload
def assert_(
    assertion: Literal[False],
    else_: Exception | type[Exception],
) -> NoReturn: ...


@overload
def assert_(
    assertion: Literal[True],
    else_: Exception | type[Exception],
) -> None: ...


@overload
def assert_(assertion: bool, else_: Exception | type[Exception]) -> None: ...  # noqa: FBT001


def assert_(assertion: bool, else_: Exception | type[Exception]) -> None:  # noqa: FBT001
    if not assertion:
        raise else_


class TrackingError(Exception): ...


@dataclass(frozen=True, unsafe_hash=False)
class Tracking[T = Any]:
    _new: list[T]
    _mutated: list[T]
    _deleted: list[T]

    def __iter__(self) -> Iterator[T]:
        return chain(self._new, self._mutated, self._deleted)

    def new(self) -> Iterable[T]:
        return self._new

    def mutated(self) -> Iterable[T]:
        return self._mutated

    def deleted(self) -> Iterable[T]:
        return self._deleted

    def register_new(self, it: T) -> None:
        if it in self._new or it in self._mutated or it in self._deleted:
            raise TrackingError

        self._new.append(it)

    def register_mutated(self, it: T) -> None:
        if it in self._new or it in self._deleted:
            raise TrackingError

        if it not in self._mutated:
            self._mutated.append(it)

    def register_deleted(self, it: T) -> None:
        if it in self._new or it in self._mutated or it in self._deleted:
            raise TrackingError

        self._deleted.append(it)
