from collections import defaultdict
from collections.abc import Iterable
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.game.ai import Ai, AiDraw, AiLoss, AiType, AiWin
from ttt.entities.core.game.board import Board
from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import (
    Game,
    GameAtomic,
    GameState,
    number_of_unfilled_cells,
)
from ttt.entities.core.game.game_result import (
    CancelledGameResult,
    DecidedGameResult,
    DrawGameResult,
    GameResult,
)
from ttt.entities.core.game.player import Player
from ttt.entities.core.game.player_result import (
    PlayerDraw,
    PlayerLoss,
    PlayerWin,
)
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.user import User
from ttt.entities.core.user.win import UserWin
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji
from ttt.infrastructure.sqlalchemy.tables.common import Base


if TYPE_CHECKING:
    from ttt.infrastructure.sqlalchemy.tables.user import TableUser


class TableAiType(StrEnum):
    gemini_2_0_flash = "gemini_2_0_flash"

    def entity(self) -> AiType:
        match self:
            case TableAiType.gemini_2_0_flash:
                return AiType.gemini_2_0_flash

    @classmethod
    def of(cls, it: AiType) -> "TableAiType":
        match it:
            case AiType.gemini_2_0_flash:
                return TableAiType.gemini_2_0_flash


ai_type = postgresql.ENUM(TableAiType, name="ai_type")


class TableAi(Base):
    __tablename__ = "ais"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    type: Mapped[TableAiType] = mapped_column(ai_type)

    def entity(self) -> Ai:
        return Ai(self.id, self.type.entity())

    @classmethod
    def of(cls, it: Ai) -> "TableAi":
        return TableAi(id=it.id, type=TableAiType.of(it.type))


class TableCell(Base):
    __tablename__ = "cells"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    board_position_x: Mapped[int]
    board_position_y: Mapped[int]
    user_filler_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    ai_filler_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )

    def entity(self) -> Cell:
        return Cell(
            self.id,
            self.game_id,
            (self.board_position_x, self.board_position_y),
            self.user_filler_id,
            self.ai_filler_id,
        )

    @classmethod
    def of(cls, it: Cell) -> "TableCell":
        return TableCell(
            id=it.id,
            game_id=it.game_id,
            board_position_x=it.board_position[0],
            board_position_y=it.board_position[1],
            user_filler_id=it.user_filler_id,
            ai_filler_id=it.ai_filler_id,
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
    user1_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    user2_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    ai1_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    ai2_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    state: Mapped[TableGameState] = mapped_column(game_state)
    player1_emoji_str: Mapped[str] = mapped_column(server_default="❌")
    player2_emoji_str: Mapped[str] = mapped_column(server_default="⭕️")

    result_decided_game_ai_win_ai_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
    )
    result_decided_game_user_win_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )
    result_decided_game_user_win_new_stars: Mapped[int | None]
    result_decided_game_user_win_rating_vector: Mapped[float | None]
    result_decided_game_ai_loss_ai_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
    )
    result_decided_game_user_loss_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )
    result_decided_game_user_loss_rating_vector: Mapped[float | None]
    result_draw_game_ai_draw1_ai_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
    )
    result_draw_game_user_draw1_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )
    result_draw_game_user_draw1_rating_vector: Mapped[float | None]
    result_draw_game_ai_draw2_ai_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
    )
    result_draw_game_user_draw2_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )
    result_draw_game_user_draw2_rating_vector: Mapped[float | None]
    result_cancelled_game_canceler_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )

    user1: Mapped["TableUser | None"] = relationship(
        lazy="joined",
        foreign_keys=[user1_id],
    )
    user2: Mapped["TableUser | None"] = relationship(
        lazy="joined",
        foreign_keys=[user2_id],
    )
    ai1: Mapped["TableAi | None"] = relationship(
        lazy="joined",
        foreign_keys=[ai1_id],
    )
    ai2: Mapped["TableAi | None"] = relationship(
        lazy="joined",
        foreign_keys=[ai2_id],
    )
    cells: Mapped[list["TableCell"]] = relationship(lazy="selectin")

    __table_args__ = (
        Index(
            "ix_games_result_decided_game_ai_win_ai_id",
            result_decided_game_ai_win_ai_id,
            postgresql_where=(result_decided_game_ai_win_ai_id.is_not(None)),
        ),
        Index(
            "ix_games_result_decided_game_user_win_user_id",
            result_decided_game_user_win_user_id,
            postgresql_where=(
                result_decided_game_user_win_user_id.is_not(None)
            ),
        ),
        Index(
            "ix_games_result_decided_game_ai_loss_ai_id",
            result_decided_game_ai_loss_ai_id,
            postgresql_where=(result_decided_game_ai_loss_ai_id.is_not(None)),
        ),
        Index(
            "ix_games_result_decided_game_user_loss_user_id",
            result_decided_game_user_loss_user_id,
            postgresql_where=result_decided_game_user_loss_user_id.is_not(None),
        ),
        Index(
            "ix_games_result_draw_game_ai_draw1_ai_id",
            result_draw_game_ai_draw1_ai_id,
            postgresql_where=result_draw_game_ai_draw1_ai_id.is_not(None),
        ),
        Index(
            "ix_games_result_draw_game_user_draw1_user_id",
            result_draw_game_user_draw1_user_id,
            postgresql_where=result_draw_game_user_draw1_user_id.is_not(None),
        ),
        Index(
            "ix_games_result_draw_game_ai_draw2_ai_id",
            result_draw_game_ai_draw2_ai_id,
            postgresql_where=result_draw_game_ai_draw2_ai_id.is_not(None),
        ),
        Index(
            "ix_games_result_draw_game_user_draw2_user_id",
            result_draw_game_user_draw2_user_id,
            postgresql_where=result_draw_game_user_draw2_user_id.is_not(None),
        ),
        Index(
            "ix_games_result_cancelled_game_canceler_id",
            result_draw_game_user_draw2_user_id,
            postgresql_where=result_draw_game_user_draw2_user_id.is_not(None),
        ),
    )

    def entity(self) -> Game:
        board = self._board(it.entity() for it in self.cells)

        return Game(
            self.id,
            self._player1(),
            Emoji(self.player1_emoji_str),
            self._player2(),
            Emoji(self.player2_emoji_str),
            board,
            number_of_unfilled_cells(board),
            self._result(),
            self.state.entity(),
        )

    def _player1(self) -> Player:
        if self.user1 is not None:
            return self.user1.entity()

        if self.ai1 is not None:
            return self.ai1.entity()

        raise ValueError

    def _player2(self) -> Player:
        if self.user2 is not None:
            return self.user2.entity()

        if self.ai2 is not None:
            return self.ai2.entity()

        raise ValueError

    def _result(self) -> GameResult | None:  # noqa: C901, PLR0912
        if self.result_cancelled_game_canceler_id is not None:
            return CancelledGameResult(self.result_cancelled_game_canceler_id)

        if (
            self.result_draw_game_user_draw1_user_id is not None
            or self.result_draw_game_ai_draw1_ai_id is not None
            or self.result_draw_game_user_draw2_user_id is not None
            or self.result_draw_game_ai_draw2_ai_id is not None
        ):
            draw1: PlayerDraw

            if self.result_draw_game_user_draw1_user_id is not None:
                draw1 = UserDraw(
                    self.result_draw_game_user_draw1_user_id,
                    self.result_draw_game_user_draw1_rating_vector,
                )
            elif self.result_draw_game_ai_draw1_ai_id is not None:
                draw1 = AiDraw(self.result_draw_game_ai_draw1_ai_id)
            else:
                raise ValueError

            draw2: PlayerDraw

            if self.result_draw_game_user_draw2_user_id is not None:
                draw2 = UserDraw(
                    self.result_draw_game_user_draw2_user_id,
                    self.result_draw_game_user_draw2_rating_vector,
                )
            elif self.result_draw_game_ai_draw2_ai_id is not None:
                draw2 = AiDraw(self.result_draw_game_ai_draw2_ai_id)
            else:
                raise ValueError

            return DrawGameResult(draw1, draw2)

        if (
            self.result_decided_game_ai_win_ai_id is not None
            or self.result_decided_game_user_win_user_id is not None
            or self.result_decided_game_ai_loss_ai_id is not None
            or self.result_decided_game_user_loss_user_id is not None
        ):
            win: PlayerWin

            if self.result_decided_game_ai_win_ai_id is not None:
                win = AiWin(self.result_decided_game_ai_win_ai_id)
            elif self.result_decided_game_user_win_user_id is not None:
                win = UserWin(
                    self.result_decided_game_user_win_user_id,
                    self.result_decided_game_user_win_new_stars,
                    self.result_decided_game_user_win_rating_vector,
                )
            else:
                raise ValueError

            loss: PlayerLoss

            if self.result_decided_game_ai_loss_ai_id is not None:
                loss = AiLoss(self.result_decided_game_ai_loss_ai_id)
            elif self.result_decided_game_user_loss_user_id is not None:
                loss = UserLoss(
                    self.result_decided_game_user_loss_user_id,
                    self.result_decided_game_user_loss_rating_vector,
                )
            else:
                raise ValueError

            return DecidedGameResult(win, loss)

        return None

    @classmethod
    def of(cls, it: Game) -> "TableGame":  # noqa: C901, PLR0912, PLR0914, PLR0915
        if isinstance(it.player1, User):
            player1_id = it.player1.id
            ai1_id = None
        else:
            player1_id = None
            ai1_id = it.player1.id

        if isinstance(it.player2, User):
            player2_id = it.player2.id
            ai2_id = None
        else:
            player2_id = None
            ai2_id = it.player2.id

        result_decided_game_ai_win_ai_id = None
        result_decided_game_user_win_user_id = None
        result_decided_game_user_win_new_stars = None
        result_decided_game_user_win_rating_vector = None
        result_decided_game_ai_loss_ai_id = None
        result_decided_game_user_loss_user_id = None
        result_decided_game_user_loss_rating_vector = None
        result_draw_game_ai_draw1_ai_id = None
        result_draw_game_user_draw1_user_id = None
        result_draw_game_user_draw1_rating_vector = None
        result_draw_game_ai_draw2_ai_id = None
        result_draw_game_user_draw2_user_id = None
        result_draw_game_user_draw2_rating_vector = None
        result_cancelled_game_canceler_id = None

        match it.result:
            case CancelledGameResult():
                result_cancelled_game_canceler_id = it.result.canceler_id
            case DrawGameResult():
                if isinstance(it.result.draw1, UserDraw):
                    result_draw_game_user_draw1_user_id = (
                        it.result.draw1.user_id
                    )
                    result_draw_game_user_draw1_rating_vector = (
                        it.result.draw1.rating_vector
                    )
                else:
                    result_draw_game_ai_draw1_ai_id = it.result.draw1.ai_id

                if isinstance(it.result.draw2, UserDraw):
                    result_draw_game_user_draw2_user_id = (
                        it.result.draw2.user_id
                    )
                    result_draw_game_user_draw2_rating_vector = (
                        it.result.draw2.rating_vector
                    )
                else:
                    result_draw_game_ai_draw2_ai_id = it.result.draw2.ai_id

            case DecidedGameResult():
                if isinstance(it.result.win, UserWin):
                    result_decided_game_user_win_user_id = it.result.win.user_id
                    result_decided_game_user_win_new_stars = (
                        it.result.win.new_stars
                    )
                    result_decided_game_user_win_rating_vector = (
                        it.result.win.rating_vector
                    )
                else:
                    result_decided_game_ai_win_ai_id = it.result.win.ai_id

                if isinstance(it.result.loss, UserLoss):
                    result_decided_game_user_loss_user_id = (
                        it.result.loss.user_id
                    )
                    result_decided_game_user_loss_rating_vector = (
                        it.result.loss.rating_vector
                    )
                else:
                    result_decided_game_ai_loss_ai_id = it.result.loss.ai_id

            case None:
                ...

        return TableGame(
            id=it.id,
            user1_id=player1_id,
            ai1_id=ai1_id,
            player1_emoji_str=it.player1_emoji.str_,
            user2_id=player2_id,
            ai2_id=ai2_id,
            player2_emoji_str=it.player2_emoji.str_,
            state=TableGameState.of(it.state),
            result_decided_game_ai_win_ai_id=result_decided_game_ai_win_ai_id,
            result_decided_game_user_win_user_id=result_decided_game_user_win_user_id,
            result_decided_game_user_win_new_stars=result_decided_game_user_win_new_stars,
            result_decided_game_user_win_rating_vector=result_decided_game_user_win_rating_vector,
            result_decided_game_ai_loss_ai_id=result_decided_game_ai_loss_ai_id,
            result_decided_game_user_loss_user_id=result_decided_game_user_loss_user_id,
            result_decided_game_user_loss_rating_vector=result_decided_game_user_loss_rating_vector,
            result_draw_game_ai_draw1_ai_id=result_draw_game_ai_draw1_ai_id,
            result_draw_game_user_draw1_user_id=result_draw_game_user_draw1_user_id,
            result_draw_game_user_draw1_rating_vector=result_draw_game_user_draw1_rating_vector,
            result_draw_game_ai_draw2_ai_id=result_draw_game_ai_draw2_ai_id,
            result_draw_game_user_draw2_user_id=result_draw_game_user_draw2_user_id,
            result_draw_game_user_draw2_rating_vector=result_draw_game_user_draw2_rating_vector,
            result_cancelled_game_canceler_id=result_cancelled_game_canceler_id,
        )

    def _board(self, cells: Iterable[Cell]) -> Board:
        cells_by_y = defaultdict[int, list[Cell]](list)

        for cell in cells:
            cells_by_y[cell.board_position[1]].append(cell)

        lines = list()

        for y in sorted(cells_by_y):
            cells_by_y[y].sort(key=lambda it: it.board_position[0])
            lines.append(cells_by_y[y])

        return Matrix(lines)


type TableGameAtomic = TableGame | TableCell | TableAi


def table_game_atomic(entity: GameAtomic) -> TableGameAtomic:
    match entity:
        case Game():
            return TableGame.of(entity)
        case Cell():
            return TableCell.of(entity)
        case Ai():
            return TableAi.of(entity)
