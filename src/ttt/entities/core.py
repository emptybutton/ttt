from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain
from uuid import UUID

from ttt.entities.math import (
    Matrix,
    Vector,
)
from ttt.entities.tools import Tracking, assert_, not_none


@dataclass
class User:
    id: int
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    tracking: Tracking

    def lose(self) -> None:
        self.number_of_defeats += 1
        self.tracking.register_mutated(self)

    def win(self) -> None:
        self.number_of_wins += 1
        self.tracking.register_mutated(self)

    def be_draw(self) -> None:
        self.number_of_draws += 1
        self.tracking.register_mutated(self)


def create_user(id_: int, tracking: Tracking) -> User:
    user = User(id_, 0, 0, 0, tracking)
    tracking.register_new(user)

    return user


class AlreadyFilledCellError(Exception): ...


@dataclass
class Cell:
    id: UUID
    game_id: UUID
    board_position: Vector
    filler_id: int | None
    tracking: Tracking

    def is_filled(self) -> bool:
        return self.filler_id is not None

    def fill(self, filler_id: int) -> None:
        """
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        assert_(not self.is_filled(), else_=AlreadyFilledCellError)
        self.filler_id = filler_id
        self.tracking.register_mutated(self)


class GameState(Enum):
    wait_player1 = auto()
    wait_player2 = auto()
    completed = auto()


type Board = Matrix[Cell]


def is_board_standard(board: Board) -> bool:
    return board.column_size() == board.line_size() == 3  # noqa: PLR2004


class InvalidCellIDMatrixError(Exception): ...


def create_empty_board(
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    tracking: Tracking,
) -> Board:
    """
    :raises ttt.entities.core.InvalidCellIDMatrixError:
    """

    assert_(cell_id_matrix.size() == (3, 3), else_=InvalidCellIDMatrixError)

    board = Matrix([
        [
            Cell(cell_id_matrix[x, y], game_id, (x, y), None, tracking)
            for x in range(3)
        ]
        for y in range(3)
    ])

    for cell in chain.from_iterable(board):
        tracking.register_new(cell)

    return board


@dataclass(frozen=True)
class GameResult:
    winner_id: int | None


class NotStandardBoardError(Exception): ...


class InvalidCellOrderError(Exception): ...


class InvalidNumberOfUnfilledCellsError(Exception): ...


class CompletedGameError(Exception): ...


class NoCellError(Exception): ...


class NotPlayerError(Exception): ...


class NotCurrentPlayerError(Exception): ...


def number_of_unfilled_cells(board: Matrix[Cell]) -> int:
    return sum(int(not cell.is_filled()) for cell in chain.from_iterable(board))


@dataclass
class Game:
    """
    :raises ttt.entities.core.NotStandardBoardError:
    :raises ttt.entities.core.InvalidCellOrderError:
    :raises ttt.entities.core.InvalidNumberOfUnfilledCellsError:
    """

    id: UUID
    player1: User
    player2: User
    board: Board
    number_of_unfilled_cells: int
    result: GameResult | None
    state: GameState
    tracking: Tracking

    def __post_init__(self) -> None:
        assert_(is_board_standard(self.board), else_=NotStandardBoardError)

        is_cell_order_ok = all(
            self.board[x, y].board_position == (x, y)
            for x in range(self.board.line_size())
            for y in range(self.board.column_size())
        )
        assert_(is_cell_order_ok, else_=InvalidCellOrderError)

        board = self.board
        assert_(
            number_of_unfilled_cells(board) == self.number_of_unfilled_cells,
            else_=InvalidNumberOfUnfilledCellsError,
        )

    def fill_cell(
        self, cell_x: int, cell_y: int, user_id: int,
    ) -> GameResult | None:
        """
        :raises ttt.entities.core.CompletedGameError:
        :raises ttt.entities.core.NotPlayerError:
        :raises ttt.entities.core.NotCurrentPlayerError:
        :raises ttt.entities.core.NoCellError:
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        current_player = self._current_player()
        current_player = not_none(current_player, else_=CompletedGameError)

        assert_(
            user_id in {self.player1.id, self.player2.id},
            else_=NotPlayerError(),
        )
        assert_(current_player.id == user_id, else_=NotCurrentPlayerError())

        try:
            cell = self.board[cell_x, cell_y]
        except KeyError as error:
            raise NoCellError from error

        cell.fill(user_id)
        self.number_of_unfilled_cells -= 1
        self.tracking.register_mutated(self)

        if self._is_player_winner(current_player, cell_x, cell_y):
            not_current_player = not_none(self._not_current_player())

            current_player.win()
            not_current_player.lose()

            return self._complete(current_player)

        if not self._can_continue():
            not_current_player = not_none(self._not_current_player())

            current_player.be_draw()
            not_current_player.be_draw()

            return self._complete(current_player)

        self._wait_next_move()
        return None

    def _can_continue(self) -> bool:
        return self.number_of_unfilled_cells >= 1

    def _is_player_winner(self, player: User, cell_x: int, cell_y: int) -> bool:
        is_winner = all(
            self.board[cell_x, y].filler_id == player.id
            for y in range(self.board.column_size())
        )
        is_winner |= all(
            int(self.board[x, cell_y].filler_id == player.id)
            for x in range(self.board.line_size())
        )

        is_winner |= {player.id} == {
            self.board[0, 0].filler_id,
            self.board[1, 1].filler_id,
            self.board[2, 2].filler_id,
        }
        is_winner |= {player.id} == {
            self.board[0, 2].filler_id,
            self.board[1, 1].filler_id,
            self.board[2, 0].filler_id,
        }

        return is_winner

    def _current_player(self) -> User | None:
        match self.state:
            case GameState.wait_player1:
                return self.player1
            case GameState.wait_player2:
                return self.player2
            case GameState.completed:
                return None

    def _not_current_player(self) -> User | None:
        match self.state:
            case GameState.wait_player1:
                return self.player2
            case GameState.wait_player2:
                return self.player1
            case GameState.completed:
                return None

    def _wait_next_move(self) -> None:
        match self.state:
            case GameState.wait_player1:
                self.state = GameState.wait_player2
            case GameState.wait_player2:
                self.state = GameState.wait_player1
            case GameState.completed:
                raise ValueError

        self.tracking.register_mutated(self)

    def _complete(self, winner: User | None) -> GameResult:
        self.result = GameResult(None if winner is None else winner.id)
        self.state = GameState.completed
        self.tracking.register_mutated(self)

        return self.result


def start_game(
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    player1: User,
    player2: User,
    tracking: Tracking,
) -> Game:
    """
    :raises ttt.entities.core.InvalidCellIDMatrixError:
    """

    board = create_empty_board(cell_id_matrix, game_id, tracking)

    game = Game(
        game_id,
        player1,
        player2,
        board,
        number_of_unfilled_cells(board),
        None,
        GameState.wait_player1,
        tracking,
    )
    tracking.register_new(game)

    return game
