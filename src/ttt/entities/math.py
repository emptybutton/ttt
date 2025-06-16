from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from ttt.entities.tools import assert_


@dataclass(frozen=True)
class InconsistentMatrixError(Exception):
    matrix: "Matrix[Any]"


type MatrixSize = tuple[int, int]
type Vector = tuple[int, int]


@dataclass
class Matrix[T]:
    """
    :raises ttt.entities.math.InconsistentMatrixError:
    """

    columns: list[list[T]]

    def size(self) -> MatrixSize:
        return self.line_size(), self.column_size()

    def line_size(self) -> int:
        if not self.columns:
            return 0

        return len(self.columns[0])

    def column_size(self) -> int:
        return len(self.columns)

    def __post_init__(self) -> None:
        line_size = self.line_size()

        assert_(
            all(len(column) == line_size for column in self.columns),
            else_=InconsistentMatrixError(self),
        )

    def __setitem__(self, x_and_y: Vector, value: T) -> None:
        x, y = x_and_y
        self.columns[y][x] = value

    def __getitem__(self, x_and_y: Vector) -> T:
        x, y = x_and_y
        return self.columns[y][x]

    def __iter__(self) -> Iterator[Iterable[T]]:
        yield from self.columns


def matrix_with_size[T](size: MatrixSize, zero: T) -> Matrix[T]:
    x, y = size

    line = [zero] * x
    columns = [line] * y

    return Matrix(columns)
