from itertools import chain
from uuid import UUID

from ttt.entities.core.game.cell import Cell
from ttt.entities.math.matrix import Matrix
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


type Board = Matrix[Cell]


def is_board_standard(board: Board) -> bool:
    return board.width() == board.height() == 3  # noqa: PLR2004


class InvalidCellIDMatrixError(Exception): ...


def create_empty_board(
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    tracking: Tracking,
) -> Board:
    """
    :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
    """

    assert_(cell_id_matrix.size() == (3, 3), else_=InvalidCellIDMatrixError)

    board = Matrix([
        [
            Cell(cell_id_matrix[x, y], game_id, (x, y), None)
            for x in range(3)
        ]
        for y in range(3)
    ])

    for cell in chain.from_iterable(board):
        tracking.register_new(cell)

    return board
