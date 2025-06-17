from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, NamedTuple

from ttt.entities.tools import assert_


@dataclass(frozen=True)
class InconsistentMatrixError(Exception):
    matrix: "Matrix[Any]"


type MatrixSize = tuple[int, int]


class Vector(NamedTuple):
    x: int
    y: int


@dataclass
class Matrix[T]:
    """
    :raises ttt.entities.math.InconsistentMatrixError:
    """

    lines: list[list[T]]

    def size(self) -> MatrixSize:
        return self.width(), self.height()

    def width(self) -> int:
        if not self.lines:
            return 0

        return len(self.lines[0])

    def height(self) -> int:
        return len(self.lines)

    def __post_init__(self) -> None:
        line_size = self.width()

        assert_(
            all(len(column) == line_size for column in self.lines),
            else_=InconsistentMatrixError(self),
        )

    def __setitem__(self, x_and_y: tuple[int, int], value: T) -> None:
        """
        :raises IndexError:
        """

        x, y = x_and_y
        self.lines[y][x] = value

    def __getitem__(self, x_and_y: tuple[int, int]) -> T:
        """
        :raises IndexError:
        """

        x, y = x_and_y
        return self.lines[y][x]

    def __iter__(self) -> Iterator[Iterable[T]]:
        yield from self.lines


def matrix_with_size[T](size: MatrixSize, zero: T) -> Matrix[T]:
    x, y = size

    line = [zero] * x
    columns = [line] * y

    return Matrix(columns)
