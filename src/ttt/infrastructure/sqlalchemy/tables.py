from abc import abstractmethod
from asyncio import gather
from collections.abc import Iterable
from enum import Enum, IntEnum, StrEnum, auto
from itertools import groupby
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ttt.entities.core.game.board import Board
from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import (
    Game,
    GameResult,
    GameState,
    number_of_unfilled_cells,
)
from ttt.entities.core.player import Player
from ttt.entities.math.matrix import Matrix
from ttt.infrastructure.sqlalchemy.loading import Loading


class Base(DeclarativeBase):
    ...


class PlayerTableModel(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    number_of_wins: Mapped[int]
    number_of_draws: Mapped[int]
    number_of_defeats: Mapped[int]
    current_game_id: Mapped[UUID | None] = mapped_column(ForeignKey("games.id"))

    def map(self, it: Player) -> None:
        self.number_of_wins = it.number_of_wins
        self.number_of_draws = it.number_of_draws
        self.number_of_defeats = it.number_of_defeats
        self.current_game_id = it.current_game_id

    async def __entity__(self, _: object) -> Player:
        return Player(
            self.id,
            self.number_of_wins,
            self.number_of_draws,
            self.number_of_defeats,
            self.current_game_id,
        )


class GameResultTableModel(Base):
    __tablename__ = "game_results"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"), unique=True)
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))

    def map(self, it: Cell) -> None:
        self.game_id = it.game_id
        self.winner_id = it.winner_id

    async def __entity__(self, _: object) -> GameResult:
        return GameResult(
            self.id,
            self.game_id,
            self.winner_id,
        )


class CellTableModel(Base):
    __tablename__ = "cells"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"))
    board_position_x: Mapped[int]
    board_position_y: Mapped[int]
    filler_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))

    def map(self, it: Cell) -> None:
        self.game_id = it.game_id
        self.board_position_x = it.board_position[0]
        self.board_position_y = it.board_position[1]
        self.filler_id = it.filler_id

    async def __entity__(self, _: object) -> Cell:
        return Cell(
            self.id,
            self.game_id,
            (self.board_position_x, self.board_position_y),
            self.filler_id,
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


class GameTableModel(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    state: Mapped[TableGameState] = mapped_column(game_state)

    cells: Mapped[list["CellTableModel"]] = relationship()
    result: Mapped["GameResultTableModel | None"] = relationship(lazy="joined")
    player1: Mapped["PlayerTableModel"] = relationship(
        lazy="joined",
        foreign_keys=[player1_id],
    )
    player2: Mapped["PlayerTableModel"] = relationship(
        lazy="joined",
        foreign_keys=[player2_id],
    )

    def map(self, it: Game) -> None:
        self.player1_id = it.player1.id
        self.player2_id = it.player2.id
        self.state = TableGameState.of(it.state)

    async def __entity__(self, loading: Loading) -> Game:
        cells, player1, player2 = await gather(
            gather(*map(loading.load, self.cells)),
            loading.load(self.player1),
            loading.load(self.player2),
        )
        board = self._board(cells)

        return Game(
            self.id,
            player1,
            player2,
            board,
            number_of_unfilled_cells(board),
            await loading.load(self.result),
            self.state.entity(),
        )

    def _board(self, cells: Iterable[Cell]) -> Board:
        groups = list(groupby(cells, key=lambda it: it.board_position[1]))

        groups.sort(key=lambda it: it[0])  # noqa: FURB118
        lines = [
            sorted(line, key=lambda it: it.board_position[0])
            for _, line in groups
        ]

        return Matrix(lines)
