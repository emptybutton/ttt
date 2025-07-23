from uuid import UUID

from pytest import FixtureRequest, fixture, mark, raises

from ttt.entities.core.game.board import Board, create_empty_board
from ttt.entities.core.game.cell import AlreadyFilledCellError, Cell
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    Game,
    GameCompletionResult,
    GameState,
    InvalidCellOrderError,
    NoCellError,
    NotCurrentPlayerError,
    NotPlayerError,
    NotStandardBoardError,
    OneEmojiError,
    OneUserError,
)
from ttt.entities.core.user.account import Account
from ttt.entities.core.user.user import User
from ttt.entities.core.user.win import UserWin
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
            [Cell(UUID(int=1), UUID(int=0), (0, 0), None, None)],
        ])

    if request.param == 3:
        return Matrix([
            [Cell(UUID(int=0), UUID(int=0), (0, 0), None, None)],
            [Cell(UUID(int=0), UUID(int=0), (0, 1), None, None)],
        ])

    if request.param == 4:
        return Matrix([
            [
                Cell(UUID(int=0), UUID(int=0), (0, 0), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 0), None, None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 1), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 1), None, None),
            ],
        ])

    if request.param == 5:
        return Matrix([
            [
                Cell(UUID(int=0), UUID(int=0), (0, 0), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 0), None, None),
                Cell(UUID(int=0), UUID(int=0), (2, 0), None, None),
                Cell(UUID(int=0), UUID(int=0), (3, 0), None, None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 1), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 1), None, None),
                Cell(UUID(int=0), UUID(int=0), (2, 1), None, None),
                Cell(UUID(int=0), UUID(int=0), (3, 1), None, None),
            ],
            [
                Cell(UUID(int=0), UUID(int=0), (0, 2), None, None),
                Cell(UUID(int=0), UUID(int=0), (1, 2), None, None),
                Cell(UUID(int=0), UUID(int=0), (2, 2), None, None),
                Cell(UUID(int=0), UUID(int=0), (3, 2), None, None),
            ],
        ])

    raise ValueError(request.param)


@fixture
def standard_board() -> Board:
    return Matrix([
        [
            Cell(UUID(int=0), UUID(int=0), (0, 0), None, None),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None, None),
            Cell(UUID(int=0), UUID(int=0), (2, 0), None, None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None, None),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None, None),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None, None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None, None),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None, None),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None, None),
        ],
    ])


@fixture
def game(
    user1: User,
    user2: User,
    emoji1: Emoji,
    emoji2: Emoji,
    standard_board: Board,
) -> Game:
    return Game(
        UUID(int=0),
        user1,
        emoji1,
        user2,
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
            Cell(UUID(int=0), UUID(int=0), (0, 0), None, None),
            Cell(UUID(int=0), UUID(int=0), (1, 0), None, None),
            Cell(UUID(int=0), UUID(int=0), (2, 7), None, None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 1), None, None),
            Cell(UUID(int=0), UUID(int=0), (1, 1), None, None),
            Cell(UUID(int=0), UUID(int=0), (2, 1), None, None),
        ],
        [
            Cell(UUID(int=0), UUID(int=0), (0, 2), None, None),
            Cell(UUID(int=0), UUID(int=0), (1, 2), None, None),
            Cell(UUID(int=0), UUID(int=0), (2, 2), None, None),
        ],
    ])


def test_not_standard_board(
    not_standard_board: Board,
    user1: User,
    user2: User,
    emoji1: Emoji,
    emoji2: Emoji,
) -> None:
    with raises(NotStandardBoardError):
        Game(
            UUID(int=0),
            user1,
            emoji1,
            user2,
            emoji2,
            not_standard_board,
            9,
            None,
            GameState.wait_player1,
        )


def test_one_user(
    user1: User,
    emoji1: Emoji,
    emoji2: Emoji,
    standard_board: Board,
) -> None:
    with raises(OneUserError):
        Game(
            UUID(int=1),
            user1,
            emoji1,
            user1,
            emoji2,
            standard_board,
            9,
            GameCompletionResult(UUID(int=8), UUID(int=0), win=None),
            GameState.wait_player1,
        )


def test_one_emoji(
    user1: User,
    user2: User,
    emoji1: Emoji,
    standard_board: Board,
) -> None:
    with raises(OneEmojiError):
        Game(
            UUID(int=1),
            user1,
            emoji1,
            user2,
            emoji1,
            standard_board,
            9,
            GameCompletionResult(UUID(int=8), UUID(int=0), win=None),
            GameState.wait_player1,
        )


def test_game_with_invalid_cell_order(
    board_with_invalid_cell_order: Board,
    user1: User,
    user2: User,
    emoji1: Emoji,
    emoji2: Emoji,
) -> None:
    with raises(InvalidCellOrderError):
        Game(
            UUID(int=0),
            user1,
            emoji1,
            user2,
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
                Cell(UUID(int=1), UUID(int=1000), (0, 0), None, None),
                Cell(UUID(int=2), UUID(int=1000), (1, 0), None, None),
                Cell(UUID(int=3), UUID(int=1000), (2, 0), None, None),
            ],
            [
                Cell(UUID(int=4), UUID(int=1000), (0, 1), None, None),
                Cell(UUID(int=5), UUID(int=1000), (1, 1), None, None),
                Cell(UUID(int=6), UUID(int=1000), (2, 1), None, None),
            ],
            [
                Cell(UUID(int=7), UUID(int=1000), (0, 2), None, None),
                Cell(UUID(int=8), UUID(int=1000), (1, 2), None, None),
                Cell(UUID(int=9), UUID(int=1000), (2, 2), None, None),
            ],
        ])

    if object_ == "tracking":
        assert len(tracking) == 9


def test_make_move_with_completed_game(  # noqa: PLR0913, PLR0917
    user1: User,
    user2: User,
    emoji1: Emoji,
    emoji2: Emoji,
    standard_board: Board,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    game = Game(
        UUID(int=1),
        user1,
        emoji1,
        user2,
        emoji2,
        standard_board,
        9,
        GameCompletionResult(UUID(int=8), UUID(int=0), win=None),
        GameState.completed,
    )

    with raises(AlreadyCompletedGameError):
        game.make_user_move(1, 1, UUID(int=8), middle_random, tracking)


def test_make_move_with_not_user(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    with raises(NotPlayerError):
        game.make_user_move(100, 9, UUID(int=8), middle_random, tracking)


def test_make_move_with_not_current_user(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    with raises(NotCurrentPlayerError):
        game.make_user_move(2, 9, UUID(int=8), middle_random, tracking)


def test_make_move_with_no_cell(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    with raises(NoCellError):
        game.make_user_move(1, 10, UUID(int=8), middle_random, tracking)


def test_make_move_with_already_filled_cell(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    game.make_user_move(1, 1, UUID(int=8), middle_random, tracking)

    with raises(AlreadyFilledCellError):
        game.make_user_move(2, 1, UUID(int=8), middle_random, tracking)


def test_make_move_with_double_move(
    game: Game,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    game.make_user_move(1, 1, UUID(int=8), middle_random, tracking)

    with raises(NotCurrentPlayerError):
        game.make_user_move(1, 2, UUID(int=8), middle_random, tracking)


@mark.parametrize("object_", ["result", "user1", "user2", "extra_move"])
def test_winning_game(  # noqa: PLR0913, PLR0917
    object_: str,
    game: Game,
    user1: User,
    user2: User,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    """
    XXX
    OOE
    ___
    """

    game.make_user_move(1, 1, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 4, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 2, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 5, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 3, UUID(int=8), middle_random, tracking)
    result = game.result

    if object_ == "result":
        assert result == GameCompletionResult(
            UUID(int=8),
            UUID(int=0),
            win=UserWin(1, 50),
        )

    if object_ == "user1":
        assert user1 == User(
            id=1,
            account=Account(50),
            emojis=[],
            stars_purchases=[],
            selected_emoji_id=None,
            number_of_wins=1,
            number_of_draws=0,
            number_of_defeats=0,
            game_location=None,
        )

    if object_ == "user2":
        assert user2 == User(
            id=2,
            account=Account(0),
            emojis=[],
            stars_purchases=[],
            selected_emoji_id=None,
            number_of_wins=0,
            number_of_draws=0,
            number_of_defeats=1,
            game_location=None,
        )

    if object_ == "extra_move":
        with raises(AlreadyCompletedGameError):
            game.make_user_move(2, 6, UUID(int=8), middle_random, tracking)


@mark.parametrize("object_", ["result", "user1", "user2", "extra_move"])
def test_drawn_game(  # noqa: PLR0913, PLR0917
    object_: str,
    game: Game,
    user1: User,
    user2: User,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    """
    XOX
    XOX
    OXO
    """

    game.make_user_move(1, 1, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 2, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 3, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 5, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 4, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 7, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 6, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 9, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 8, UUID(int=8), middle_random, tracking)
    result = game.result

    if object_ == "result":
        assert result == GameCompletionResult(
            UUID(int=8),
            UUID(int=0),
            win=None,
        )

    if object_ == "user1":
        assert user1 == User(
            id=1,
            account=Account(0),
            emojis=[],
            stars_purchases=[],
            selected_emoji_id=None,
            number_of_wins=0,
            number_of_draws=1,
            number_of_defeats=0,
            game_location=None,
        )

    if object_ == "user2":
        assert user2 == User(
            id=2,
            account=Account(0),
            emojis=[],
            stars_purchases=[],
            selected_emoji_id=None,
            number_of_wins=0,
            number_of_draws=1,
            number_of_defeats=0,
            game_location=None,
        )

    if object_ == "extra_move":
        with raises(AlreadyCompletedGameError):
            game.make_user_move(2, 5, UUID(int=8), middle_random, tracking)


@mark.parametrize("object_", ["result", "user1", "user2", "extra_move"])
def test_winning_game_with_filled_board(  # noqa: PLR0913, PLR0917
    object_: str,
    game: Game,
    user1: User,
    user2: User,
    middle_random: Random,
    tracking: Tracking,
) -> None:
    """
    XOX
    OXO
    XXO
    """

    game.make_user_move(1, 1, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 2, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 3, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 4, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 5, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 6, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 8, UUID(int=8), middle_random, tracking)
    game.make_user_move(2, 9, UUID(int=8), middle_random, tracking)

    game.make_user_move(1, 7, UUID(int=8), middle_random, tracking)
    result = game.result

    if object_ == "result":
        assert result == GameCompletionResult(
            UUID(int=8),
            UUID(int=0),
            UserWin(1, 50),
        )

    if object_ == "user1":
        assert user1 == User(
            id=1,
            account=Account(50),
            emojis=[],
            stars_purchases=[],
            selected_emoji_id=None,
            number_of_wins=1,
            number_of_draws=0,
            number_of_defeats=0,
            game_location=None,
        )

    if object_ == "user2":
        assert user2 == User(
            id=2,
            account=Account(0),
            emojis=[],
            stars_purchases=[],
            selected_emoji_id=None,
            number_of_wins=0,
            number_of_draws=0,
            number_of_defeats=1,
            game_location=None,
        )

    if object_ == "extra_move":
        with raises(AlreadyCompletedGameError):
            game.make_user_move(2, 5, UUID(int=8), middle_random, tracking)
