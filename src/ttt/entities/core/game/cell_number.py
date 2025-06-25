from dataclasses import dataclass
from typing import ClassVar, cast

from ttt.entities.math.vector import Vector
from ttt.entities.tools.assertion import assert_, not_none


class InvalidCellNumberError(Exception): ...


@dataclass(frozen=True)
class CellNumber:
    """
    :raises ttt.entities.core.game.cell_number.InvalidCellNumberError:
    """

    _int: int

    _board_position_by_int: ClassVar = {
        1: (0, 0),
        2: (1, 0),
        3: (2, 0),
        4: (0, 1),
        5: (1, 1),
        6: (2, 1),
        7: (0, 2),
        8: (1, 2),
        9: (2, 2),
    }
    _int_by_board_position: ClassVar = dict(zip(
        _board_position_by_int.values(),
        _board_position_by_int.keys(),
        strict=True,
    ))

    def __post_init__(self) -> None:
        assert_(1 <= self._int <= 9, else_=InvalidCellNumberError)  # noqa: PLR2004

    def __int__(self) -> int:
        return self._int

    @classmethod
    def of_board_position(cls, board_position: Vector) -> "CellNumber":
        int_ = CellNumber._int_by_board_position.get(board_position)
        int_ = cast(int, not_none(int_, InvalidCellNumberError))

        return CellNumber(int_)

    def board_position(self) -> "Vector":
        return cast(Vector, CellNumber._board_position_by_int[int(self)])
