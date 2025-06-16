from uuid import UUID

from pytest import FixtureRequest, fixture, mark, raises

from ttt.entities.core import (
    Board,
    Cell,
    Game,
    GameState,
    InvalidCellOrderError,
    NotStandardBoardError,
    User,
    create_empty_board,
)
from ttt.entities.math import (
    Matrix,
)
from ttt.entities.tools import Tracking


@fixture
def tracking() -> Tracking:
    return Tracking()


@fixture(params=range(6))
def not_standard_board(request: FixtureRequest, tracking: Tracking) -> Board:
    if request.param == 0:
        return Matrix([])

    if request.param == 1:
        return Matrix([[]])

    if request.param == 2:
        return Matrix([
            [Cell(UUID(int=1), UUID(int=0), (0, 0), None, tracking)],
        ])

    if request.param == 3:
        return Matrix([
            [Cell(UUID(int=0), UUID(int=0), (0, 0), None, tracking)],
            [Cell(UUID(int=0), UUID(int=0), (0, 1), None, tracking)],
        ])

    if request.param == 4:
        return Matrix([
            [
                Cell(UUID(int=0), UUID(int=0), (0, 0), None, tracking),
                Cell(UUID(int=0), UUID(int=0), (1, 0), None, tracking),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 1), None, tracking),
                Cell(UUID(int=0), UUID(int=0), (1, 1), None, tracking),
            ],
        ])

    if request.param == 5:
        return Matrix([
        [
            Cell(UUID(int=0), UUID(int=0), (0, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (3, 0), None, tracking),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (3, 1), None, tracking),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (3, 2), None, tracking),
        ],
    ])

    raise ValueError(request.param)


@fixture
def standard_board(tracking: Tracking) -> Board:
    return Matrix([
        [
            Cell(UUID(int=0), UUID(int=0), (0, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 0), None, tracking),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None, tracking),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None, tracking),
        ],
    ])


def test_not_standard_board(
    tracking: Tracking,
    not_standard_board: Board,
) -> None:
    with raises(NotStandardBoardError):
        Game(
            UUID(int=0),
            User(0, 1, 2, 3, tracking),
            User(1, 1, 2, 3, tracking),
            not_standard_board,
            9,
            None,
            GameState.wait_player1,
            tracking,
        )


@fixture
def board_with_invalid_cell_order(tracking: Tracking) -> Board:
    return Matrix([
        [
            Cell(UUID(int=0), UUID(int=0), (0, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 7), None, tracking),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None, tracking),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None, tracking),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None, tracking),
        ],
    ])


def test_game_with_invalid_cell_order(
    tracking: Tracking, board_with_invalid_cell_order: Board,
) -> None:
    with raises(InvalidCellOrderError):
        Game(
            UUID(int=0),
            User(0, 1, 2, 3, tracking),
            User(1, 1, 2, 3, tracking),
            board_with_invalid_cell_order,
            9,
            None,
            GameState.wait_player1,
            tracking,
        )


@mark.parametrize("object_", ["board", "tracking"])
def test_create_empty_board_ok(tracking: Tracking, object_: str) -> None:
    board = create_empty_board(
        Matrix([
            [UUID(int=1), UUID(int=2), UUID(int=3)],
            [UUID(int=4), UUID(int=5), UUID(int=6)],
            [UUID(int=7), UUID(int=8), UUID(int=9)],
        ]),
        UUID(int=1000),
        tracking,
    )

    if object_ == "board":
        assert board == Matrix([
            [
                Cell(UUID(int=1), UUID(int=1000), (0, 0), None, tracking),
                Cell(UUID(int=2), UUID(int=1000), (1, 0), None, tracking),
                Cell(UUID(int=3), UUID(int=1000), (2, 0), None, tracking),
            ],
            [
                Cell(UUID(int=4), UUID(int=1000), (0, 1), None, tracking),
                Cell(UUID(int=5), UUID(int=1000), (1, 1), None, tracking),
                Cell(UUID(int=6), UUID(int=1000), (2, 1), None, tracking),
            ],
            [
                Cell(UUID(int=7), UUID(int=1000), (0, 2), None, tracking),
                Cell(UUID(int=8), UUID(int=1000), (1, 2), None, tracking),
                Cell(UUID(int=9), UUID(int=1000), (2, 2), None, tracking),
            ],
        ])

    if object_ == "tracking":
        assert len(tracking) == 9
