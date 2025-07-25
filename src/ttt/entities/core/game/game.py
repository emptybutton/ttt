from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain
from uuid import UUID

from ttt.entities.core.game.ai import Ai, AiType, create_ai
from ttt.entities.core.game.board import (
    Board,
    create_empty_board,
    is_board_standard,
)
from ttt.entities.core.game.cell import AlreadyFilledCellError, Cell
from ttt.entities.core.game.cell_number import (
    CellNumber,
    InvalidCellNumberError,
)
from ttt.entities.core.game.player import Player
from ttt.entities.core.game.win import Win
from ttt.entities.core.user.user import (
    User,
    UserAlreadyInGameError,
)
from ttt.entities.math.matrix import Matrix
from ttt.entities.math.random import Random, choice
from ttt.entities.math.vector import Vector
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import assert_, none, not_none
from ttt.entities.tools.tracking import Tracking


class GameState(Enum):
    wait_player1 = auto()
    wait_player2 = auto()
    completed = auto()


@dataclass(frozen=True)
class GameCompletionResult:
    id: UUID
    game_id: UUID
    win: Win | None


@dataclass(frozen=True)
class GameCancellationResult:
    id: UUID
    game_id: UUID
    canceler_id: int


type GameResult = GameCompletionResult | GameCancellationResult


@dataclass(frozen=True)
class UserMove:
    next_move_ai_id: UUID | None
    filled_cell_number: CellNumber


@dataclass(frozen=True)
class AiMove:
    was_random: bool
    filled_cell_number: CellNumber


class OneUserError(Exception): ...


class NotStandardBoardError(Exception): ...


class InvalidCellOrderError(Exception): ...


class InvalidNumberOfUnfilledCellsError(Exception): ...


class AlreadyCompletedGameError(Exception): ...


class NoCellError(Exception): ...


class NotPlayerError(Exception): ...


class NotCurrentPlayerError(Exception): ...


class OneEmojiError(Exception): ...


class SameRandomEmojiError(Exception): ...


class OnlyAiGameError(Exception): ...


class NotAiCurrentMoveError(Exception): ...


def number_of_unfilled_cells(board: Matrix[Cell]) -> int:
    return sum(int(not cell.is_filled()) for cell in chain.from_iterable(board))


@dataclass
class Game:
    """
    :raises ttt.entities.core.game.game.OnlyAiGameError:
    :raises ttt.entities.core.game.game.OneEmojiError:
    :raises ttt.entities.core.game.game.OneUserError:
    :raises ttt.entities.core.game.game.NotStandardBoardError:
    :raises ttt.entities.core.game.game.InvalidCellOrderError:
    :raises ttt.entities.core.game.game.InvalidNumberOfUnfilledCellsError:
    """

    id: UUID
    player1: Player
    player1_emoji: Emoji
    player2: Player
    player2_emoji: Emoji
    board: Board
    number_of_unfilled_cells: int
    result: GameResult | None
    state: GameState

    def __post_init__(self) -> None:
        assert_(
            not all(isinstance(player, Ai) for player in self._players()),
            else_=OnlyAiGameError,
        )

        if isinstance(self.player1, User) and isinstance(self.player2, User):
            assert_(self.player1.id != self.player2.id, else_=OneUserError)

        assert_(self.player1_emoji != self.player2_emoji, else_=OneEmojiError)
        assert_(is_board_standard(self.board), else_=NotStandardBoardError)

        is_cell_order_ok = all(
            self.board[x, y].board_position == (x, y)
            for x in range(self.board.width())
            for y in range(self.board.height())
        )
        assert_(is_cell_order_ok, else_=InvalidCellOrderError)

        board = self.board
        assert_(
            number_of_unfilled_cells(board) == self.number_of_unfilled_cells,
            else_=InvalidNumberOfUnfilledCellsError,
        )

    def is_against_ai(self) -> bool:
        return isinstance(self.player1, Ai) or isinstance(self.player2, Ai)

    def is_against_user(self) -> bool:
        return not self.is_against_ai()

    def is_completed(self) -> bool:
        return self.result is not None

    def cancel(
        self,
        user_id: int,
        game_result_id: UUID,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.game.game.AlreadyCompletedGameError:
        :raises ttt.entities.core.game.game.NotPlayerError:
        """

        none(self.result, else_=AlreadyCompletedGameError)
        canceler = not_none(self._user(user_id), else_=NotPlayerError)

        if isinstance(self.player1, User):
            self.player1.leave_game(tracking)
        if isinstance(self.player2, User):
            self.player2.leave_game(tracking)

        self.result = GameCancellationResult(
            game_result_id,
            self.id,
            canceler.id,
        )
        tracking.register_new(self.result)
        self.state = GameState.completed
        tracking.register_mutated(self)

    def make_user_move(
        self,
        user_id: int,
        cell_number_int: int,
        game_result_id: UUID,
        player_win_random: Random,
        tracking: Tracking,
    ) -> UserMove:
        """
        :raises ttt.entities.core.game.game.AlreadyCompletedGameError:
        :raises ttt.entities.core.game.game.NotPlayerError:
        :raises ttt.entities.core.game.game.NotCurrentPlayerError:
        :raises ttt.entities.core.game.game.NoCellError:
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        current_player = not_none(
            self._current_player(),
            AlreadyCompletedGameError,
        )
        if not isinstance(current_player, User):
            raise TypeError

        not_current_player = not_none(self._not_current_player())

        assert_(
            user_id in {user.id for user in self._users()},
            else_=NotPlayerError(),
        )
        assert_(current_player.id == user_id, else_=NotCurrentPlayerError())

        try:
            cell_number = CellNumber(cell_number_int)
        except InvalidCellNumberError as error:
            raise NoCellError from error
        else:
            cell_position = cell_number.board_position()

        try:
            cell = self.board[cell_position]
        except IndexError as error:
            raise NoCellError from error

        cell.fill_as_user(user_id, tracking)
        self.number_of_unfilled_cells -= 1
        tracking.register_mutated(self)

        if self._is_player_winner(current_player, cell.board_position):
            if self.is_against_ai():
                win = current_player.win_against_ai(tracking)
            else:
                win = current_player.win_against_user(
                    player_win_random,
                    tracking,
                )

            if isinstance(not_current_player, User):
                not_current_player.lose(tracking)

            self._complete(win, game_result_id, tracking)

        elif not self._can_continue():
            current_player.be_draw(tracking)

            if isinstance(not_current_player, User):
                not_current_player.be_draw(tracking)

            self._complete(
                win=None,
                game_result_id=game_result_id,
                tracking=tracking,
            )

        else:
            self._wait_next_move(tracking)

        next_move_player = self._current_player()
        next_move_ai_id = (
            next_move_player.id if isinstance(next_move_player, Ai) else None
        )

        return UserMove(
            next_move_ai_id=next_move_ai_id,
            filled_cell_number=cell.number(),
        )

    def make_ai_move(
        self,
        ai_id: UUID,
        cell_number_int: int | None,
        game_result_id: UUID,
        free_cell_random: Random,
        tracking: Tracking,
    ) -> AiMove:
        """
        :raises ttt.entities.core.game.game.AlreadyCompletedGameError:
        :raises ttt.entities.core.game.game.NotAiCurrentMoveError:
        """

        current_player = not_none(
            self._current_player(),
            AlreadyCompletedGameError,
        )
        if not isinstance(current_player, Ai):
            raise NotAiCurrentMoveError

        not_current_player = self._not_current_player()
        if not isinstance(not_current_player, User):
            raise TypeError

        if cell_number_int is None:
            return self._make_random_ai_move(
                current_player,
                not_current_player,
                free_cell_random,
                game_result_id,
                tracking,
            )

        try:
            cell_number = CellNumber(cell_number_int)
        except InvalidCellNumberError:
            return self._make_random_ai_move(
                current_player,
                not_current_player,
                free_cell_random,
                game_result_id,
                tracking,
            )
        else:
            cell_position = cell_number.board_position()

        try:
            cell = self.board[cell_position]
        except IndexError:
            return self._make_random_ai_move(
                current_player,
                not_current_player,
                free_cell_random,
                game_result_id,
                tracking,
            )

        try:
            cell.fill_as_ai(ai_id, tracking)
        except AlreadyFilledCellError:
            return self._make_random_ai_move(
                current_player,
                not_current_player,
                free_cell_random,
                game_result_id,
                tracking,
            )

        self.number_of_unfilled_cells -= 1
        tracking.register_mutated(self)

        if self._is_player_winner(current_player, cell_position):
            win = current_player.win()
            not_current_player.lose(tracking)

            self._complete(win, game_result_id, tracking)

        elif not self._can_continue():
            not_current_player.be_draw(tracking)

            self._complete(
                win=None,
                game_result_id=game_result_id,
                tracking=tracking,
            )

        else:
            self._wait_next_move(tracking)

        return AiMove(was_random=False, filled_cell_number=cell.number())

    def _make_random_ai_move(
        self,
        current_player: Ai,
        not_current_player: User,
        free_cell_random: Random,
        game_result_id: UUID,
        tracking: Tracking,
    ) -> AiMove:
        cell = choice(self._free_cells(), random=free_cell_random)
        cell.fill_as_ai(current_player.id, tracking)
        self.number_of_unfilled_cells -= 1
        tracking.register_mutated(self)

        if self._is_player_winner(current_player, cell.board_position):
            win = current_player.win()
            not_current_player.lose(tracking)

            self._complete(win, game_result_id, tracking)

        elif not self._can_continue():
            not_current_player.be_draw(tracking)

            self._complete(
                win=None,
                game_result_id=game_result_id,
                tracking=tracking,
            )

        else:
            self._wait_next_move(tracking)

        return AiMove(was_random=True, filled_cell_number=cell.number())

    def _free_cells(self) -> tuple[Cell, ...]:
        return tuple(
            cell for line in self.board for cell in line if cell.is_free()
        )

    def _can_continue(self) -> bool:
        return not self._is_board_filled()

    def _is_board_filled(self) -> bool:
        return self.number_of_unfilled_cells <= 0

    def _is_player_winner(self, player: Player, cell_position: Vector) -> bool:
        cell_x, cell_y = cell_position

        is_winner = all(
            self.board[cell_x, y].filler_id() == player.id
            for y in range(self.board.height())
        )
        is_winner |= all(
            int(self.board[x, cell_y].filler_id() == player.id)
            for x in range(self.board.width())
        )

        is_winner |= {player.id} == {
            self.board[0, 0].filler_id(),
            self.board[1, 1].filler_id(),
            self.board[2, 2].filler_id(),
        }
        is_winner |= {player.id} == {
            self.board[0, 2].filler_id(),
            self.board[1, 1].filler_id(),
            self.board[2, 0].filler_id(),
        }

        return is_winner

    def _current_player(self) -> Player | None:
        match self.state:
            case GameState.wait_player1:
                return self.player1
            case GameState.wait_player2:
                return self.player2
            case GameState.completed:
                return None

    def _user(self, user_id: int) -> User | None:
        for user in self._users():
            if user.id == user_id:
                return user

        return None

    def _players(self) -> tuple[Player, ...]:
        return self.player1, self.player2

    def _users(self) -> tuple[User, ...]:
        return tuple(
            player for player in self._players() if isinstance(player, User)
        )

    def _not_current_player(self) -> Player | None:
        match self.state:
            case GameState.wait_player1:
                return self.player2
            case GameState.wait_player2:
                return self.player1
            case GameState.completed:
                return None

    def _wait_next_move(self, tracking: Tracking) -> None:
        match self.state:
            case GameState.wait_player1:
                self.state = GameState.wait_player2
            case GameState.wait_player2:
                self.state = GameState.wait_player1
            case GameState.completed:
                raise ValueError

        tracking.register_mutated(self)

    def _complete(
        self,
        win: Win | None,
        game_result_id: UUID,
        tracking: Tracking,
    ) -> None:
        self.result = GameCompletionResult(game_result_id, self.id, win)
        tracking.register_new(self.result)
        self.state = GameState.completed
        tracking.register_mutated(self)


type GameAtomic = Game | GameResult | Cell | Ai


@dataclass(frozen=True)
class UsersAlreadyInGameError(Exception):
    users: Sequence[User]


def start_game(  # noqa: PLR0913, PLR0917
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    player1: User,
    player1_random_emoji: Emoji,
    player2: User,
    player2_random_emoji: Emoji,
    tracking: Tracking,
) -> Game:
    """
    :raises ttt.entities.core.game.game.SameRandomEmojiError:
    :raises ttt.entities.core.game.game.OneUserError:
    :raises ttt.entities.core.game.game.UsersAlreadyInGameError:
    :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
    """

    assert_(player1_random_emoji != player2_random_emoji, SameRandomEmojiError)

    player1_emoji = player1.emoji(player1_random_emoji)
    player2_emoji = player2.emoji(player2_random_emoji)

    if player1_emoji == player2_emoji:
        player1_emoji = player1_random_emoji
        player2_emoji = player2_random_emoji

    board = create_empty_board(cell_id_matrix, game_id, tracking)
    game = Game(
        game_id,
        player1,
        player1_emoji,
        player2,
        player2_emoji,
        board,
        number_of_unfilled_cells(board),
        None,
        GameState.wait_player1,
    )
    tracking.register_new(game)

    players_in_game = []

    try:
        player1.be_in_game(game_id, tracking)
    except UserAlreadyInGameError:
        players_in_game.append(player1)

    try:
        player2.be_in_game(game_id, tracking)
    except UserAlreadyInGameError:
        players_in_game.append(player2)

    if players_in_game:
        raise UsersAlreadyInGameError(players_in_game)

    return game


@dataclass(frozen=True, unsafe_hash=False)
class StartedGameWithAi:
    game: Game
    next_move_ai_id: UUID | None


def start_game_with_ai(  # noqa: PLR0913, PLR0917
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    user: User,
    user_random_emoji: Emoji,
    ai_id: UUID,
    ai_type: AiType,
    ai_random_emoji: Emoji,
    player_order_random: Random,
    tracking: Tracking,
) -> StartedGameWithAi:
    """
    :raises ttt.entities.core.game.game.SameRandomEmojiError:
    :raises ttt.entities.core.game.game.UserAlreadyInGameError:
    :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
    """

    assert_(user_random_emoji != ai_random_emoji, SameRandomEmojiError)

    user_emoji = user.emoji(user_random_emoji)
    ai_emoji = ai_random_emoji

    if user_emoji == ai_random_emoji:
        user_emoji = user_random_emoji

    ai = create_ai(ai_id, ai_type, tracking)

    player1: Player
    player2: Player

    if float(player_order_random) >= 0.5:  # noqa: PLR2004
        player1, player2 = user, ai
        player1_emoji, player2_emoji = user_emoji, ai_emoji
        next_move_ai_id = None
    else:
        player1, player2 = ai, user
        player1_emoji, player2_emoji = ai_emoji, user_emoji
        next_move_ai_id = player1.id

    board = create_empty_board(cell_id_matrix, game_id, tracking)
    game = Game(
        game_id,
        player1,
        player1_emoji,
        player2,
        player2_emoji,
        board,
        number_of_unfilled_cells(board),
        None,
        GameState.wait_player1,
    )
    tracking.register_new(game)

    user.be_in_game(game_id, tracking)

    return StartedGameWithAi(game, next_move_ai_id)
