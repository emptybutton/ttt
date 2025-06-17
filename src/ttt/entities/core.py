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
class Player:
    id: int
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    current_game_id: UUID | None

    def be_in_game(self, game_id: UUID) -> None:
        self.current_game_id = game_id

    def lose(self, tracking: Tracking) -> None:
        self.current_game_id = None
        self.number_of_defeats += 1
        tracking.register_mutated(self)

    def win(self, tracking: Tracking) -> None:
        self.current_game_id = None
        self.number_of_wins += 1
        tracking.register_mutated(self)

    def be_draw(self, tracking: Tracking) -> None:
        self.current_game_id = None
        self.number_of_draws += 1
        tracking.register_mutated(self)


def create_player(id_: int, tracking: Tracking) -> Player:
    player = Player(id_, 0, 0, 0, None)
    tracking.register_new(player)

    return player


class AlreadyFilledCellError(Exception): ...


@dataclass
class Cell:
    id: UUID
    game_id: UUID
    board_position: Vector
    filler_id: int | None

    def is_filled(self) -> bool:
        return self.filler_id is not None

    def fill(self, filler_id: int, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        assert_(not self.is_filled(), else_=AlreadyFilledCellError)
        self.filler_id = filler_id
        tracking.register_mutated(self)


class GameState(Enum):
    wait_player1 = auto()
    wait_player2 = auto()
    completed = auto()


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
    :raises ttt.entities.core.InvalidCellIDMatrixError:
    """

    assert_(cell_id_matrix.size() == (3, 3), else_=InvalidCellIDMatrixError)

    board = Matrix([
        [
            Cell(cell_id_matrix[x, y], game_id, Vector(x, y), None)
            for x in range(3)
        ]
        for y in range(3)
    ])

    for cell in chain.from_iterable(board):
        tracking.register_new(cell)

    return board


@dataclass(frozen=True)
class GameResult:
    id: UUID
    game_id: UUID
    winner_id: int | None


class OnePlayerError(Exception): ...


class NotStandardBoardError(Exception): ...


class InvalidCellOrderError(Exception): ...


class InvalidNumberOfUnfilledCellsError(Exception): ...


@dataclass(frozen=True)
class CompletedGameError(Exception):
    game_result: GameResult


class NoCellError(Exception): ...


class NotPlayerError(Exception): ...


class NotCurrentPlayerError(Exception): ...


def number_of_unfilled_cells(board: Matrix[Cell]) -> int:
    return sum(int(not cell.is_filled()) for cell in chain.from_iterable(board))


@dataclass
class Game:
    """
    :raises ttt.entities.core.OnePlayerError:
    :raises ttt.entities.core.NotStandardBoardError:
    :raises ttt.entities.core.InvalidCellOrderError:
    :raises ttt.entities.core.InvalidNumberOfUnfilledCellsError:
    """

    id: UUID
    player1: Player
    player2: Player
    board: Board
    number_of_unfilled_cells: int
    result: GameResult | None
    state: GameState

    def __post_init__(self) -> None:
        assert_(self.player1.id != self.player2.id, else_=OnePlayerError)
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

    def make_move(
        self,
        player_id: int,
        cell_position: Vector,
        game_result_id: UUID,
        tracking: Tracking,
    ) -> GameResult | None:
        """
        :raises ttt.entities.core.CompletedGameError:
        :raises ttt.entities.core.NotPlayerError:
        :raises ttt.entities.core.NotCurrentPlayerError:
        :raises ttt.entities.core.NoCellError:
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        current_player = self._current_player()

        if current_player is None:
            raise CompletedGameError(not_none(self.result))

        assert_(
            player_id in {self.player1.id, self.player2.id},
            else_=NotPlayerError(),
        )
        assert_(current_player.id == player_id, else_=NotCurrentPlayerError())

        self._fill_cell(cell_position, player_id, tracking)

        if self._is_player_winner(current_player, cell_position):
            not_current_player = not_none(self._not_current_player())

            current_player.win(tracking)
            not_current_player.lose(tracking)

            return self._complete(game_result_id, current_player, tracking)

        if not self._can_continue():
            not_current_player = not_none(self._not_current_player())

            current_player.be_draw(tracking)
            not_current_player.be_draw(tracking)

            return self._complete(game_result_id, None, tracking)

        self._wait_next_move(tracking)
        return None

    def _fill_cell(
        self, cell_position: Vector, player_id: int, tracking: Tracking,
    ) -> GameResult | None:
        """
        :raises ttt.entities.core.NoCellError:
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        try:
            cell = self.board[cell_position]
        except IndexError as error:
            raise NoCellError from error

        cell.fill(player_id, tracking)
        self.number_of_unfilled_cells -= 1
        tracking.register_mutated(self)

    def _can_continue(self) -> bool:
        return not self._is_board_filled()

    def _is_board_filled(self) -> bool:
        return self.number_of_unfilled_cells <= 0

    def _is_player_winner(self, player: Player, cell_position: Vector) -> bool:
        cell_x, cell_y = cell_position

        is_winner = all(
            self.board[cell_x, y].filler_id == player.id
            for y in range(self.board.height())
        )
        is_winner |= all(
            int(self.board[x, cell_y].filler_id == player.id)
            for x in range(self.board.width())
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

    def _current_player(self) -> Player | None:
        match self.state:
            case GameState.wait_player1:
                return self.player1
            case GameState.wait_player2:
                return self.player2
            case GameState.completed:
                return None

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
        self, game_result_id: UUID, winner: Player | None, tracking: Tracking,
    ) -> GameResult:
        self.result = GameResult(
            game_result_id, self.id, None if winner is None else winner.id,
        )
        self.state = GameState.completed
        tracking.register_mutated(self)

        return self.result


@dataclass(frozen=True)
class PlayerAlreadyInGameError(Exception):
    players: tuple[Player, ...]


def start_game(
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    player1: Player,
    player2: Player,
    tracking: Tracking,
) -> Game:
    """
    :raises ttt.entities.core.PlayerAlreadyInGameError:
    :raises ttt.entities.core.InvalidCellIDMatrixError:
    :raises ttt.entities.core.OnePlayerError:
    """

    players_in_game = tuple(
        player
        for player in (player1, player2)
        if player.current_game_id is not None
    )
    assert_(
        not players_in_game,
        else_=PlayerAlreadyInGameError(players_in_game),
    )

    board = create_empty_board(cell_id_matrix, game_id, tracking)

    game = Game(
        game_id,
        player1,
        player2,
        board,
        number_of_unfilled_cells(board),
        None,
        GameState.wait_player1,
    )
    tracking.register_new(game)

    player1.be_in_game(game_id)
    player2.be_in_game(game_id)

    return game
