from collections.abc import Sequence
from dataclasses import dataclass

from ttt.entities.tools.assertion import assert_


class InvalidFactorRangeError(Exception): ...


@dataclass(frozen=True)
class Random:
    """
    :raises ttt.entities.math.random.InvalidFactorRangeError:
    """

    _float: float

    def __post_init__(self) -> None:
        assert_(0 <= self._float <= 1, else_=InvalidFactorRangeError)

    def __float__(self) -> float:
        return self._float


def randrange(stop: int, *, random: Random) -> int:
    return int(stop * float(random))


def deviated_int(base: int, deviating: int, *, random: Random) -> int:
    return base - deviating // 2 + randrange(deviating, random=random)


def choice[T](values: Sequence[T], *, random: Random) -> T:
    index = randrange(len(values) - 1, random=random)
    return values[index]
