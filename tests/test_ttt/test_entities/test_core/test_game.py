from uuid import UUID

from pytest import FixtureRequest, fixture, mark, raises

from ttt.entities.core.game.board import Board, create_empty_board
from ttt.entities.core.game.cell import AlreadyFilledCellError, Cell
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    Game,
    GameResult,
    GameState,
    InvalidCellOrderError,
    NoCellError,
    NotCurrentPlayerError,
    NotPlayerError,
    NotStandardBoardError,
    OneEmojiError,
    OnePlayerError,
)
from ttt.entities.core.player.account import Account
from ttt.entities.core.player.player import Player
from ttt.entities.core.player.win import Win
from ttt.entities.math.matrix import Matrix
from ttt.entities.math.random import Random
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.tracking import Tracking


@fixture(params=range(6))
def not_standard_board(request: FixtureRequest) -> Board:
    if request.param == 0:
        return Matrix([])

    if request.param == 1:
        return Matrix([[]])

    if request.param == 2:
        return Matrix([
            [Cell(UUID(int=1), UUID(int=0), (0, 0), None)],
        ])

    if request.param == 3:
        return Matrix([
            [Cell(UUID(int=0), UUID(int=0), (0, 0), None)],
            [Cell(UUID(int=0), UUID(int=0), (0, 1), None)],
        ])

    if request.param == 4:
        return Matrix([
            [
                Cell(UUID(int=0), UUID(int=0), (0, 0), None),
                Cell(UUID(int=0), UUID(int=0), (1, 0), None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 1), None),
                Cell(UUID(int=0), UUID(int=0), (1, 1), None),
            ],
        ])

    if request.param == 5:
        return Matrix([
            [
                Cell(UUID(int=0), UUID(int=0), (0, 0), None),
                Cell(UUID(int=0), UUID(int=0), (1, 0), None),
                Cell(UUID(int=0), UUID(int=0), (2, 0), None),
                Cell(UUID(int=0), UUID(int=0), (3, 0), None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 1), None),
                Cell(UUID(int=0), UUID(int=0), (1, 1), None),
                Cell(UUID(int=0), UUID(int=0), (2, 1), None),
                Cell(UUID(int=0), UUID(int=0), (3, 1), None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 2), None),
                Cell(UUID(int=0), UUID(int=0), (1, 2), None),
                Cell(UUID(int=0), UUID(int=0), (2, 2), None),
                Cell(UUID(int=0), UUID(int=0), (3, 2), None),
            ],
        ])

    raise ValueError(request.param)


@fixture
def standard_board() -> Board:
    return Matrix([
        [
            Cell(UUID(int=0), UUID(int=0), (0, 0), None),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None),
            Cell(UUID(int=0), UUID(int=0), (2, 0), None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None),
        ],
    ])


@fixture
def game(
    player1: Player,
    player2: Player,
    emoji1: Emoji,
    emoji2: Emoji,
    standard_board: Board,
) -> Game:
    return Game(
        UUID(int=0),
        player1,
        emoji1,
        player2,
        emoji2,
        standard_board,
        9,
        None,
        GameState.wait_player1,
    )


@fixture
def board_with_invalid_cell_order() -> Board:
    return Matrix([
        [
            Cell(UUID(int=0), UUID(int=0), (0, 0), None),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None),
            Cell(UUID(int=0), UUID(int=0), (2, 7), None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None),
        ],
    ])


def test_not_standard_board(
    not_standard_board: Board,
    player1: Player,
    player2: Player,
    emoji1: Emoji,
    emoji2: Emoji,
) -> None:
    with raises(NotStandardBoardError):
        Game(
            UUID(int=0),
            player1,
            emoji1,
            player2,
            emoji2,
            not_standard_board,
            9,
            None,
            GameState.wait_player1,
        )


def test_one_player(
    player1: Player,
    emoji1: Emoji,
    emoji2: Emoji,
    standard_board: Board,
) -> None:
    with raises(OnePlayerError):
        Game(
            UUID(int=1),
            player1,
            emoji1,
            player1,
            emoji2,
            standard_board,
            9,
            GameResult(UUID(int=8), UUID(int=0), win=None),
            GameState.wait_player1,
        )


def test_one_emoji(
    player1: Player,
    player2: Player,
    emoji1: Emoji,
    standard_board: Board,
) -> None:
    with raises(OneEmojiError):
        Game(
            UUID(int=1),
            player1,
            emoji1,
            player2,
            emoji1,
            standard_board,
            9,
            GameResult(UUID(int=8), UUID(int=0), win=None),
            GameState.wait_player1,
        )


def test_game_with_invalid_cell_order(
    board_with_invalid_cell_order: Board,
    player1: Player,
    player2: Player,
    emoji1: Emoji,
    emoji2: Emoji,
) -> None:
    with raises(InvalidCellOrderError):
        Game(
            UUID(int=0),
            player1,
            emoji1,
            player2,
            emoji2,
            board_with_invalid_cell_order,
            9,
            None,
            GameState.wait_player1,
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
                Cell(UUID(int=1), UUID(int=1000), (0, 0), None),
                Cell(UUID(int=2), UUID(int=1000), (1, 0), None),
                Cell(UUID(int=3), UUID(int=1000), (2, 0), None),
            ],
            [
                Cell(UUID(int=4), UUID(int=1000), (0, 1), None),
                Cell(UUID(int=5), UUID(int=1000), (1, 1), None),
                Cell(UUID(int=6), UUID(int=1000), (2, 1), None),
            ],
            [
                Cell(UUID(int=7), UUID(int=1000), (0, 2), None),
                Cell(UUID(int=8), UUID(int=1000), (1, 2), None),
                Cell(UUID(int=9), UUID(int=1000), (2, 2), None),
            ],
        ])

    if object_ == "tracking":
        assert len(tracking) == 9


def test_make_move_with_completed_game(  # noqa: PLR0913, PLR0917
    player1: Player,
    player2: Player,
    emoji1: Emoji,
    emoji2: Emoji,
    standard_board: Board,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    game = Game(
        UUID(int=1),
        player1,
        emoji1,
        player2,
        emoji2,
        standard_board,
        9,
        GameResult(UUID(int=8), UUID(int=0), win=None),
        GameState.completed,
    )

    with raises(AlreadyCompletedGameError):
        game.make_move(1, (0, 0), UUID(int=8), middle_random, tracking)


def test_make_move_with_not_player(
    game: Game, middle_random: Random, tracking: Tracking,
) -> None:
    with raises(NotPlayerError):
        game.make_move(100, (2, 2), UUID(int=8), middle_random, tracking)


def test_make_move_with_not_current_player(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    with raises(NotCurrentPlayerError):
        game.make_move(2, (2, 2), UUID(int=8), middle_random, tracking)


def test_make_move_with_no_cell(
    game: Game, middle_random: Random, tracking: Tracking,
) -> None:
    with raises(NoCellError):
        game.make_move(1, (3, 1), UUID(int=8), middle_random, tracking)


def test_make_move_with_already_filled_cell(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    game.make_move(1, (0, 0), UUID(int=8), middle_random, tracking)

    with raises(AlreadyFilledCellError):
        game.make_move(2, (0, 0), UUID(int=8), middle_random, tracking)


def test_make_move_with_double_move(
    game: Game, middle_random: Random, tracking: Tracking,
) -> None:
    game.make_move(1, (0, 0), UUID(int=8), middle_random, tracking)

    with raises(NotCurrentPlayerError):
        game.make_move(1, (1, 0), UUID(int=8), middle_random, tracking)


@mark.parametrize("object_", ["result", "player1", "player2", "extra_move"])
def test_winning_game(  # noqa: PLR0913, PLR0917
    object_: str,
    game: Game,
    player1: Player,
    player2: Player,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    """
    XXX
    OOE
    ___
    """

    game.make_move(1, (0, 0), UUID(int=8), middle_random, tracking)
    game.make_move(2, (0, 1), UUID(int=8), middle_random, tracking)

    game.make_move(1, (1, 0), UUID(int=8), middle_random, tracking)
    game.make_move(2, (1, 1), UUID(int=8), middle_random, tracking)

    game.make_move(1, (2, 0), UUID(int=8), middle_random, tracking)
    result = game.result

    if object_ == "result":
        assert result == GameResult(UUID(int=8), UUID(int=0), win=Win(1, 50))

    if object_ == "player1":
        assert player1 == Player(1, Account(50), 1, 0, 0, None)

    if object_ == "player2":
        assert player2 == Player(2, Account(0), 0, 0, 1, None)

    if object_ == "extra_move":
        with raises(AlreadyCompletedGameError):
            game.make_move(2, (2, 1), UUID(int=8), middle_random, tracking)


@mark.parametrize("object_", ["result", "player1", "player2", "extra_move"])
def test_drawn_game(  # noqa: PLR0913, PLR0917
    object_: str,
    game: Game,
    player1: Player,
    player2: Player,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    """
    XOX
    XOX
    OXO
    """

    game.make_move(1, (0, 0), UUID(int=8), middle_random, tracking)
    game.make_move(2, (1, 0), UUID(int=8), middle_random, tracking)

    game.make_move(1, (2, 0), UUID(int=8), middle_random, tracking)
    game.make_move(2, (1, 1), UUID(int=8), middle_random, tracking)

    game.make_move(1, (0, 1), UUID(int=8), middle_random, tracking)
    game.make_move(2, (0, 2), UUID(int=8), middle_random, tracking)

    game.make_move(1, (2, 1), UUID(int=8), middle_random, tracking)
    game.make_move(2, (2, 2), UUID(int=8), middle_random, tracking)

    game.make_move(1, (1, 2), UUID(int=8), middle_random, tracking)
    result = game.result

    if object_ == "result":
        assert result == GameResult(UUID(int=8), UUID(int=0), win=None)

    if object_ == "player1":
        assert player1 == Player(1, Account(0), 0, 1, 0, None)

    if object_ == "player2":
        assert player2 == Player(2, Account(0), 0, 1, 0, None)

    if object_ == "extra_move":
        with raises(AlreadyCompletedGameError):
            game.make_move(2, (2, 1), UUID(int=8), middle_random, tracking)


@mark.parametrize("object_", ["result", "player1", "player2", "extra_move"])
def test_winning_game_with_filled_board(  # noqa: PLR0913, PLR0917
    object_: str,
    game: Game,
    player1: Player,
    player2: Player,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    """
    XOX
    OXO
    XXO
    """

    game.make_move(1, (0, 0), UUID(int=8), middle_random, tracking)
    game.make_move(2, (1, 0), UUID(int=8), middle_random, tracking)

    game.make_move(1, (2, 0), UUID(int=8), middle_random, tracking)
    game.make_move(2, (0, 1), UUID(int=8), middle_random, tracking)

    game.make_move(1, (1, 1), UUID(int=8), middle_random, tracking)
    game.make_move(2, (2, 1), UUID(int=8), middle_random, tracking)

    game.make_move(1, (1, 2), UUID(int=8), middle_random, tracking)
    game.make_move(2, (2, 2), UUID(int=8), middle_random, tracking)

    game.make_move(1, (0, 2), UUID(int=8), middle_random, tracking)
    result = game.result

    if object_ == "result":
        assert result == GameResult(UUID(int=8), UUID(int=0), Win(1, 50))

    if object_ == "player1":
        assert player1 == Player(1, Account(50), 1, 0, 0, None)

    if object_ == "player2":
        assert player2 == Player(2, Account(0), 0, 0, 1, None)

    if object_ == "extra_move":
        with raises(AlreadyCompletedGameError):
            game.make_move(2, (2, 1), UUID(int=8), middle_random, tracking)
