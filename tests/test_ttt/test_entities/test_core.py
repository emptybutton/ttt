from uuid import UUID

from pytest import FixtureRequest, fixture, mark, raises

from ttt.entities.core import (
    AlreadyFilledCellError,
    Board,
    Cell,
    CompletedGameError,
    Game,
    GameResult,
    GameState,
    InvalidCellOrderError,
    NoCellError,
    NotCurrentPlayerError,
    NotPlayerError,
    NotStandardBoardError,
    OnePlayerError,
    Player,
    create_empty_board,
    create_player,
)
from ttt.entities.math import (
    Matrix,
)
from ttt.entities.tools import Tracking


@fixture
def tracking() -> Tracking:
    return Tracking()


@fixture
def player1(tracking: Tracking) -> Player:
    return Player(1, 0, 0, 0, tracking)


@fixture
def player2(tracking: Tracking) -> Player:
    return Player(2, 0, 0, 0, tracking)


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


@fixture
def game(
    tracking: Tracking,
    player1: Player,
    player2: Player,
    standard_board: Board,
) -> Game:
    return Game(
        UUID(int=0),
        player1,
        player2,
        standard_board,
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


def test_not_standard_board(
    tracking: Tracking,
    not_standard_board: Board,
) -> None:
    with raises(NotStandardBoardError):
        Game(
            UUID(int=0),
            Player(0, 1, 2, 3, tracking),
            Player(1, 1, 2, 3, tracking),
            not_standard_board,
            9,
            None,
            GameState.wait_player1,
            tracking,
        )


def test_make_move_with_one_player(
    player1: Player,
    standard_board: Board,
    tracking: Tracking,
) -> None:
    with raises(OnePlayerError):
        Game(
            UUID(int=1),
            player1,
            player1,
            standard_board,
            9,
            GameResult(None),
            GameState.wait_player1,
            tracking,
        )


def test_game_with_invalid_cell_order(
    tracking: Tracking,
    board_with_invalid_cell_order: Board,
) -> None:
    with raises(InvalidCellOrderError):
        Game(
            UUID(int=0),
            Player(0, 1, 2, 3, tracking),
            Player(1, 1, 2, 3, tracking),
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


def test_make_move_with_completed_game(
    player1: Player,
    player2: Player,
    standard_board: Board,
    tracking: Tracking,
) -> None:
    game = Game(
        UUID(int=1),
        player1,
        player2,
        standard_board,
        9,
        GameResult(None),
        GameState.completed,
        tracking,
    )

    with raises(CompletedGameError):
        game.make_move(1, (0, 0))


def test_make_move_with_not_player(game: Game) -> None:
    with raises(NotPlayerError):
        game.make_move(100, (2, 2))


def test_make_move_with_not_current_player(game: Game) -> None:
    with raises(NotCurrentPlayerError):
        game.make_move(2, (2, 2))


def test_make_move_with_no_cell(game: Game) -> None:
    with raises(NoCellError):
        game.make_move(1, (3, 1))


def test_make_move_with_already_filled_cell(game: Game) -> None:
    game.make_move(1, (0, 0))

    with raises(AlreadyFilledCellError):
        game.make_move(2, (0, 0))


def test_make_move_with_double_move(game: Game) -> None:
    game.make_move(1, (0, 0))

    with raises(NotCurrentPlayerError):
        game.make_move(1, (1, 0))


@mark.parametrize("object_", ["result", "player1", "player2", "extra_move"])
def test_winning_game(
    object_: str, game: Game, player1: Player, player2: Player, tracking: Tracking,
) -> None:
    """
    XXX
    OOE
    ___
    """

    game.make_move(1, (0, 0))
    game.make_move(2, (0, 1))

    game.make_move(1, (1, 0))
    game.make_move(2, (1, 1))

    result = game.make_move(1, (2, 0))

    if object_ == "result":
        assert result == GameResult(winner_id=1)

    if object_ == "player1":
        assert player1 == Player(1, 1, 0, 0, tracking)

    if object_ == "player2":
        assert player2 == Player(2, 0, 0, 1, tracking)

    if object_ == "extra_move":
        with raises(CompletedGameError):
            game.make_move(2, (2, 1))


@mark.parametrize("object_", ["result", "player1", "player2", "extra_move"])
def test_drawn_game(
    object_: str, game: Game, player1: Player, player2: Player, tracking: Tracking,
) -> None:
    """
    XOX
    XOX
    OXO
    """

    game.make_move(1, (0, 0))
    game.make_move(2, (1, 0))

    game.make_move(1, (2, 0))
    game.make_move(2, (1, 1))

    game.make_move(1, (0, 1))
    game.make_move(2, (0, 2))

    game.make_move(1, (2, 1))
    game.make_move(2, (2, 2))

    result = game.make_move(1, (1, 2))

    if object_ == "result":
        assert result == GameResult(winner_id=None)

    if object_ == "player1":
        assert player1 == Player(1, 0, 1, 0, tracking)

    if object_ == "player2":
        assert player2 == Player(2, 0, 1, 0, tracking)

    if object_ == "extra_move":
        with raises(CompletedGameError):
            game.make_move(2, (2, 1))


@mark.parametrize("object_", ["result", "player1", "player2", "extra_move"])
def test_winning_game_with_filled_board(
    object_: str, game: Game, player1: Player, player2: Player, tracking: Tracking,
) -> None:
    """
    XOX
    OXO
    XXO
    """

    game.make_move(1, (0, 0))
    game.make_move(2, (1, 0))

    game.make_move(1, (2, 0))
    game.make_move(2, (0, 1))

    game.make_move(1, (1, 1))
    game.make_move(2, (2, 1))

    game.make_move(1, (1, 2))
    game.make_move(2, (2, 2))

    result = game.make_move(1, (0, 2))

    if object_ == "result":
        assert result == GameResult(winner_id=1)

    if object_ == "player1":
        assert player1 == Player(1, 1, 0, 0, tracking)

    if object_ == "player2":
        assert player2 == Player(2, 0, 0, 1, tracking)

    if object_ == "extra_move":
        with raises(CompletedGameError):
            game.make_move(2, (2, 1))


@mark.parametrize("object_", ["player", "tracking"])
def test_create_player(tracking: Tracking, object_: str) -> None:
    player = create_player(42, tracking)

    if object_ == "player":
        assert player == Player(42, 0, 0, 0, tracking)

    if object_ == "tracking":
        assert len(tracking) == 1
