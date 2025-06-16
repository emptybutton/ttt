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

    _columns: list[list[T]]

    def size(self) -> MatrixSize:
        return self.line_size(), self.column_size()

    def line_size(self) -> int:
        if not self._columns:
            return 0

        return len(self._columns[0])

    def column_size(self) -> int:
        return len(self._columns)

    def __post_init__(self) -> None:
        x_size = self.line_size()

        assert_(
            all(len(column) == x_size for column in self._columns),
            else_=InconsistentMatrixError(self),
        )

    def __setitem__(self, x_and_y: Vector, value: T) -> None:
        x, y = x_and_y
        self._columns[y][x] = value

    def __getitem__(self, x_and_y: Vector) -> T:
        x, y = x_and_y
        return self._columns[y][x]
