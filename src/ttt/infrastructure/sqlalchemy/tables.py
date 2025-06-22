from collections import defaultdict
from collections.abc import Iterable
from enum import StrEnum
from itertools import groupby
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ttt.entities.aggregate import Aggregate
from ttt.entities.core.game.board import Board
from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import (
    Game,
    GameResult,
    GameState,
    number_of_unfilled_cells,
)
from ttt.entities.core.player.location import PlayerGameLocation
from ttt.entities.core.player.player import Player
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji


class Base(DeclarativeBase): ...


class TablePlayer(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    number_of_wins: Mapped[int]
    number_of_draws: Mapped[int]
    number_of_defeats: Mapped[int]
    game_location_game_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
    )
    game_location_chat_id: Mapped[int | None] = mapped_column(BigInteger())

    def entity(self) -> Player:
        if (
            self.game_location_game_id is not None
            and self.game_location_chat_id is not None
        ):
            location = PlayerGameLocation(
                self.id,
                self.game_location_chat_id,
                self.game_location_game_id,
            )
        else:
            location = None

        return Player(
            self.id,
            self.number_of_wins,
            self.number_of_draws,
            self.number_of_defeats,
            location,
        )

    @classmethod
    def of(cls, it: Player) -> "TablePlayer":
        if it.game_location is None:
            game_location_game_id = None
            game_location_chat_id = None
        else:
            game_location_game_id = it.game_location.game_id
            game_location_chat_id = it.game_location.chat_id

        return TablePlayer(
            id=it.id,
            number_of_wins=it.number_of_wins,
            number_of_draws=it.number_of_draws,
            number_of_defeats=it.number_of_defeats,
            game_location_game_id=game_location_game_id,
            game_location_chat_id=game_location_chat_id,
        )


class TableGameResult(Base):
    __tablename__ = "game_results"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"), unique=True)
    winner_id: Mapped[int | None] = mapped_column(
        BigInteger(), ForeignKey("players.id"),
    )

    def entity(self) -> GameResult:
        return GameResult(
            self.id,
            self.game_id,
            self.winner_id,
        )

    @classmethod
    def of(cls, it: GameResult) -> "TableGameResult":
        return TableGameResult(
            id=it.id,
            game_id=it.game_id,
            winner_id=it.winner_id,
        )


class TableCell(Base):
    __tablename__ = "cells"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"))
    board_position_x: Mapped[int]
    board_position_y: Mapped[int]
    filler_id: Mapped[int | None] = mapped_column(
        BigInteger(), ForeignKey("players.id"),
    )

    def entity(self) -> Cell:
        return Cell(
            self.id,
            self.game_id,
            (self.board_position_x, self.board_position_y),
            self.filler_id,
        )

    @classmethod
    def of(cls, it: Cell) -> "TableCell":
        return TableCell(
            id=it.id,
            game_id=it.game_id,
            board_position_x=it.board_position[0],
            board_position_y=it.board_position[1],
            filler_id=it.filler_id,
        )


class TableGameState(StrEnum):
    wait_player1 = "wait_player1"
    wait_player2 = "wait_player2"
    completed = "completed"

    def entity(self) -> GameState:
        match self:
            case TableGameState.wait_player1:
                return GameState.wait_player1

            case TableGameState.wait_player2:
                return GameState.wait_player2

            case TableGameState.completed:
                return GameState.completed

    @classmethod
    def of(cls, it: GameState) -> "TableGameState":
        match it:
            case GameState.wait_player1:
                return TableGameState.wait_player1

            case GameState.wait_player2:
                return TableGameState.wait_player2

            case GameState.completed:
                return TableGameState.completed


game_state = postgresql.ENUM(TableGameState, name="game_state")


class TableGame(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    player1_id: Mapped[int] = mapped_column(
        BigInteger(), ForeignKey("players.id"),
    )
    player2_id: Mapped[int] = mapped_column(
        BigInteger(), ForeignKey("players.id"),
    )
    state: Mapped[TableGameState] = mapped_column(game_state)

    result: Mapped["TableGameResult | None"] = relationship(lazy="joined")
    player1: Mapped["TablePlayer"] = relationship(
        lazy="joined",
        foreign_keys=[player1_id],
    )
    player1_emoji_str: Mapped[str] = mapped_column(server_default="❌")
    player2: Mapped["TablePlayer"] = relationship(
        lazy="joined",
        foreign_keys=[player2_id],
    )
    player2_emoji_str: Mapped[str] = mapped_column(server_default="⭕️")
    cells: Mapped[list["TableCell"]] = relationship(lazy="selectin")

    def entity(self) -> Game:
        board = self._board(it.entity() for it in self.cells)
        player1 = self.player1.entity()
        player2 = self.player2.entity()

        return Game(
            self.id,
            player1,
            Emoji(self.player1_emoji_str),
            player2,
            Emoji(self.player2_emoji_str),
            board,
            number_of_unfilled_cells(board),
            None if self.result is None else self.result.entity(),
            self.state.entity(),
        )

    @classmethod
    def of(cls, it: Game) -> "TableGame":
        return TableGame(
            id=it.id,
            player1_id=it.player1.id,
            player1_emoji_char=it.player1_emoji.str_,
            player2_id=it.player2.id,
            player2_emoji_char=it.player2_emoji.str_,
            state=TableGameState.of(it.state),
        )

    def _board(self, cells: Iterable[Cell]) -> Board:
        cells_by_y = defaultdict[int, list[Cell]](list)

        for cell in cells:
            cells_by_y[cell.board_position[1]].append(cell)

        for y_cells in cells_by_y.values():
            y_cells.sort(key=lambda it: it.board_position[0])

        return Matrix(list(cells_by_y.values()))


type TablePlayerAggregate = TablePlayer

type TableGameAggregate = TableGame | TableGameResult | TableCell

type TableAggregate = TablePlayerAggregate | TableGameAggregate


def table_entity(entity: Aggregate) -> TableAggregate:
    match entity:
        case Player():
            return TablePlayer.of(entity)

        case Game():
            return TableGame.of(entity)
        case GameResult():
            return TableGameResult.of(entity)
        case Cell():
            return TableCell.of(entity)
