from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain
from typing import cast
from uuid import UUID

from ttt.entities.core.game.board import (
    Board,
    create_empty_board,
    is_board_standard,
)
from ttt.entities.core.game.cell import AlreadyFilledCellError, Cell
from ttt.entities.core.player.player import (
    Player,
    PlayerAlreadyInGameError,
)
from ttt.entities.core.player.win import Win
from ttt.entities.math.matrix import Matrix
from ttt.entities.math.random import Random
from ttt.entities.math.vector import Vector
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import assert_, not_none
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


class OnePlayerError(Exception): ...


class NotStandardBoardError(Exception): ...


class InvalidCellOrderError(Exception): ...


class InvalidNumberOfUnfilledCellsError(Exception): ...


class AlreadyCompletedGameError(Exception): ...


class NoCellError(Exception): ...


class NotPlayerError(Exception): ...


class NotCurrentPlayerError(Exception): ...


class OneEmojiError(Exception): ...


def number_of_unfilled_cells(board: Matrix[Cell]) -> int:
    return sum(int(not cell.is_filled()) for cell in chain.from_iterable(board))


type FilledCellPosition = None


@dataclass
class Game:
    """
    :raises ttt.entities.core.game.game.OneEmojiError:
    :raises ttt.entities.core.game.game.OnePlayerError:
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
        assert_(self.player1.id != self.player2.id, else_=OnePlayerError)
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

    def cancel(
        self, player_id: int, game_result_id: UUID, tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.game.game.AlreadyCompletedGameError:
        :raises ttt.entities.core.game.game.NotPlayerError:
        """

        self.result = cast(
            GameResult, not_none(self.result, AlreadyCompletedGameError),
        )
        canceler = not_none(self._player(player_id), else_=NotPlayerError)

        self.player1.leave_game(tracking)
        self.player2.leave_game(tracking)

        self.result = GameCancellationResult(
            game_result_id, self.id, canceler.id,
        )
        tracking.register_new(self.result)
        self.state = GameState.completed
        tracking.register_mutated(self)

    def make_move(
        self,
        player_id: int,
        cell_position: Vector | FilledCellPosition,
        game_result_id: UUID,
        random: Random,
        tracking: Tracking,
    ) -> GameResult | None:
        """
        :raises ttt.entities.core.game.game.AlreadyCompletedGameError:
        :raises ttt.entities.core.game.game.NotPlayerError:
        :raises ttt.entities.core.game.game.NotCurrentPlayerError:
        :raises ttt.entities.core.game.game.NoCellError:
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        current_player = not_none(
            self._current_player(), AlreadyCompletedGameError,
        )
        assert_(
            player_id in {self.player1.id, self.player2.id},
            else_=NotPlayerError(),
        )
        assert_(current_player.id == player_id, else_=NotCurrentPlayerError())

        if cell_position is None:
            raise AlreadyFilledCellError

        self._fill_cell(cell_position, player_id, tracking)

        if self._is_player_winner(current_player, cell_position):
            not_current_player = not_none(self._not_current_player())

            win = current_player.win(random, tracking)
            not_current_player.lose(tracking)

            self._complete(win, game_result_id, tracking)
            return None

        if not self._can_continue():
            not_current_player = not_none(self._not_current_player())

            current_player.be_draw(tracking)
            not_current_player.be_draw(tracking)

            self._complete(None, game_result_id, tracking)
            return None

        self._wait_next_move(tracking)
        return None

    def _fill_cell(
        self, cell_position: Vector, player_id: int, tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.core.game.game.NoCellError:
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
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

    def _player(self, player_id: int) -> Player | None:
        match player_id:
            case self.player1.id:
                return self.player1
            case self.player2.id:
                return self.player2
            case _:
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
        self, win: Win | None, game_result_id: UUID, tracking: Tracking,
    ) -> None:
        self.result = GameCompletionResult(game_result_id, self.id, win)
        tracking.register_new(self.result)
        self.state = GameState.completed
        tracking.register_mutated(self)


type GameAggregate = Game | GameResult | Cell


@dataclass(frozen=True)
class PlayersAlreadyInGameError(Exception):
    players: Sequence[Player]


def start_game(  # noqa: PLR0913, PLR0917
    cell_id_matrix: Matrix[UUID],
    game_id: UUID,
    player1: Player,
    player1_emoji: Emoji,
    player1_chat_id: int,
    player2: Player,
    player2_emoji: Emoji,
    player2_chat_id: int,
    tracking: Tracking,
) -> Game:
    """
    :raises ttt.entities.core.game.game.OneEmojiError:
    :raises ttt.entities.core.game.game.OnePlayerError:
    :raises ttt.entities.core.game.game.PlayersAlreadyInGameError:
    :raises ttt.entities.core.game.board.InvalidCellIDMatrixError:
    """

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
        player1.be_in_game(game_id, player1_chat_id, tracking)
    except PlayerAlreadyInGameError:
        players_in_game.append(player1)

    try:
        player2.be_in_game(game_id, player2_chat_id, tracking)
    except PlayerAlreadyInGameError:
        players_in_game.append(player2)

    if players_in_game:
        raise PlayersAlreadyInGameError(players_in_game)

    return game
