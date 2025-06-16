from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from ttt.entities.math import (
    Matrix,
    Vector,
)
from ttt.entities.tools import Tracking, assert_, not_none


@dataclass
class User:
    _id: int
    _number_of_wins: int
    _number_of_draws: int
    _number_of_defeats: int
    _tracking: Tracking

    def id(self) -> int:
        return self._id

    def lose(self) -> None:
        self._number_of_defeats += 1
        self._tracking.register_mutated(self)

    def win(self) -> None:
        self._number_of_wins += 1
        self._tracking.register_mutated(self)

    def be_draw(self) -> None:
        self._number_of_draws += 1
        self._tracking.register_mutated(self)


def create_user(id_: int, tracking: Tracking) -> User:
    user = User(id_, 0, 0, 0, tracking)
    tracking.register_new(user)

    return user


class AlreadyFilledCellError(Exception): ...


@dataclass
class Cell:
    _id: UUID
    _game_id: UUID
    _board_position: Vector
    _filler_id: int | None
    _tracking: Tracking

    def board_position(self) -> Vector:
        return self._board_position

    def is_filled(self) -> bool:
        return self._filler_id is not None

    def filler_id(self) -> int | None:
        return self._filler_id

    def fill(self, filler_id: int) -> None:
        """
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        assert_(not self.is_filled(), else_=AlreadyFilledCellError)
        self._filler_id = filler_id
        self._tracking.register_mutated(self)


class GameState(Enum):
    wait_player1 = auto()
    wait_player2 = auto()
    completed = auto()


type Board = Matrix[Cell]


def is_board_standard(board: Board) -> bool:
    return board.column_size() == board.line_size() == 3  # noqa: PLR2004


@dataclass(frozen=True)
class GameResult:
    winner_id: int


class NotStandardBoardError(Exception): ...


class InvalidCellOrderError(Exception): ...


class CompletedGameError(Exception): ...


class NoCellError(Exception): ...


class NotPlayerError(Exception): ...


class NotCurrentPlayerError(Exception): ...


@dataclass
class Game:
    """
    :raises ttt.entities.core.NotStandardBoardError:
    :raises ttt.entities.core.InvalidCellOrderError:
    """

    _id: UUID
    _player1: User
    _player2: User
    _board: Matrix[Cell]
    _number_of_unfilled_cells: int
    _result: GameResult
    _state: GameState
    _tracking: Tracking

    def __post_init__(self) -> None:
        assert_(is_board_standard(self._board), else_=NotStandardBoardError)

        is_cell_order_ok = all(
            self._board[x, y].board_position() == (x, y)
            for x in range(self._board.line_size())
            for y in range(self._board.column_size())
        )
        assert_(is_cell_order_ok, else_=InvalidCellOrderError)

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
            user_id == self._player1.id() or user_id == self._player2.id(),
            else_=NotPlayerError(),
        )
        assert_(current_player.id() == user_id, else_=NotCurrentPlayerError())

        try:
            cell = self._board[cell_x, cell_y]
        except KeyError as error:
            raise NoCellError from error

        cell.fill(user_id)
        self._number_of_unfilled_cells -= 1
        self._tracking.register_mutated(self)

        if self._is_player_winner(current_player, cell_x, cell_y):
            not_current_player = not_none(self._not_current_player())

            current_player.win()
            not_current_player.lose()

            self._complete(current_player)
            return None

        if not self._can_continue():
            not_current_player = not_none(self._not_current_player())

            current_player.be_draw()
            not_current_player.be_draw()

            self._complete(current_player)
            return None

        self._wait_next_move()
        return None

    def _can_continue(self) -> bool:
        return self._number_of_unfilled_cells >= 1

    def _is_player_winner(self, player: User, cell_x: int, cell_y: int) -> bool:
        is_winner = all(
            self._board[cell_x, y].filler_id() == player.id()
            for y in range(self._board.column_size())
        )
        is_winner |= all(
            int(self._board[x, cell_y].filler_id() == player.id())
            for x in range(self._board.line_size())
        )

        is_winner |= {player.id()} == {
            self._board[0, 0].filler_id(),
            self._board[1, 1].filler_id(),
            self._board[2, 2].filler_id(),
        }
        is_winner |= {player.id()} == {
            self._board[0, 2].filler_id(),
            self._board[1, 1].filler_id(),
            self._board[2, 0].filler_id(),
        }

        return is_winner

    def _current_player(self) -> User | None:
        match self._state:
            case GameState.wait_player1:
                return self._player1
            case GameState.wait_player2:
                return self._player2
            case GameState.completed:
                return None

    def _not_current_player(self) -> User | None:
        match self._state:
            case GameState.wait_player1:
                return self._player2
            case GameState.wait_player2:
                return self._player1
            case GameState.completed:
                return None

    def _wait_next_move(self) -> None:
        match self._state:
            case GameState.wait_player1:
                self._state = GameState.wait_player2
            case GameState.wait_player2:
                self._state = GameState.wait_player1
            case GameState.completed:
                raise ValueError

        self._tracking.register_mutated(self)

    def _complete(self, winner: User) -> None:
        self._result = GameResult(winner.id())
        self._state = GameState.completed
        self._tracking.register_mutated(self)
