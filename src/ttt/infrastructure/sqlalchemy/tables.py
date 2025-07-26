from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CHAR, BigInteger, ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ttt.entities.atomic import Atomic
from ttt.entities.core.game.ai import Ai, AiDraw, AiLoss, AiType, AiWin
from ttt.entities.core.game.board import Board
from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import (
    Game,
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
from ttt.entities.core.game.player_result import PlayerDraw, PlayerLoss, PlayerWin
from ttt.entities.core.user.account import Account
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.emoji import UserEmoji
from ttt.entities.core.user.last_game import LastGame
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.stars_purchase import StarsPurchase
from ttt.entities.core.user.user import User
from ttt.entities.core.user.win import UserWin
from ttt.entities.finance.payment.payment import Payment, PaymentState
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.finance.rubles import Rubles
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji


class Base(DeclarativeBase): ...


class TablePaymentState(StrEnum):
    in_process = "in_process"
    cancelled = "cancelled"
    completed = "completed"

    def entity(self) -> PaymentState:
        match self:
            case TablePaymentState.in_process:
                return PaymentState.in_process
            case TablePaymentState.cancelled:
                return PaymentState.cancelled
            case TablePaymentState.completed:
                return PaymentState.completed

    @classmethod
    def of(cls, it: PaymentState) -> "TablePaymentState":
        match it:
            case PaymentState.in_process:
                return TablePaymentState.in_process
            case PaymentState.cancelled:
                return TablePaymentState.cancelled
            case PaymentState.completed:
                return TablePaymentState.completed


payment_state = postgresql.ENUM(TablePaymentState, name="payment_state")


class TablePayment(Base):
    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    paid_rubles_total_kopecks: Mapped[int] = mapped_column(BigInteger())
    start_datetime: Mapped[datetime]
    completion_datetime: Mapped[datetime | None]
    success_id: Mapped[str | None]
    success_gateway_id: Mapped[str | None]
    state: Mapped[TablePaymentState] = mapped_column(payment_state)

    def entity(self) -> Payment:
        if self.success_id is None or self.success_gateway_id is None:
            success = None
        else:
            success = PaymentSuccess(self.success_id, self.success_gateway_id)

        paid_rubles = Rubles.with_total_kopecks(
            self.paid_rubles_total_kopecks,
        )

        return Payment(
            id_=self.id,
            paid_rubles=paid_rubles,
            start_datetime=self.start_datetime,
            completion_datetime=self.completion_datetime,
            success=success,
            state=self.state.entity(),
        )

    @classmethod
    def of(cls, it: Payment) -> "TablePayment":
        if it.success is None:
            success_id = None
            success_gateway_id = None
        else:
            success_id = it.success.id
            success_gateway_id = it.success.gateway_id

        return TablePayment(
            id=it.id_,
            paid_rubles_total_kopecks=it.paid_rubles.total_kopecks(),
            start_datetime=it.start_datetime,
            completion_datetime=it.completion_datetime,
            success_id=success_id,
            success_gateway_id=success_gateway_id,
            state=TablePaymentState.of(it.state),
        )


class TableUserEmoji(Base):
    __tablename__ = "user_emojis"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    emoji_str: Mapped[str] = mapped_column(CHAR(1))
    datetime_of_purchase: Mapped[datetime]

    def entity(self) -> UserEmoji:
        return UserEmoji(
            self.id,
            self.user_id,
            Emoji(self.emoji_str),
            self.datetime_of_purchase,
        )

    @classmethod
    def of(cls, it: UserEmoji) -> "TableUserEmoji":
        return TableUserEmoji(
            id=it.id,
            user_id=it.user_id,
            emoji_str=it.emoji.str_,
            datetime_of_purchase=it.datetime_of_purchase,
        )


class TableStarsPurchase(Base):
    __tablename__ = "stars_purchases"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    stars: Mapped[int]
    payment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("payments.id", deferrable=True, initially="DEFERRED"),
    )

    payment: Mapped[TablePayment | None] = relationship(
        TablePayment,
        lazy="joined",
    )

    __table_args__ = (
        Index(
            "ix_stars_purchases_payment_id",
            payment_id,
            postgresql_where=(payment_id.is_not(None)),
        ),
    )

    def entity(self) -> StarsPurchase:
        return StarsPurchase(
            id_=self.id,
            user_id=self.user_id,
            stars=self.stars,
            payment=None if self.payment is None else self.payment.entity(),
        )

    @classmethod
    def of(cls, it: StarsPurchase) -> "TableStarsPurchase":
        return TableStarsPurchase(
            id=it.id_,
            user_id=it.user_id,
            stars=it.stars,
            payment_id=None if it.payment is None else it.payment.id_,
        )


class TableLastGame(Base):
    __tablename__ = "last_games"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )
    game_id: Mapped[UUID] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
    )

    def entity(self) -> LastGame:
        return LastGame(
            id=self.id,
            user_id=self.user_id,
            game_id=self.game_id,
        )

    @classmethod
    def of(cls, it: LastGame) -> "TableLastGame":
        return TableLastGame(
            id=it.id,
            user_id=it.user_id,
            game_id=it.game_id,
        )


class TableUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger(),
        primary_key=True,
        autoincrement=False,
    )
    account_stars: Mapped[int] = mapped_column(server_default="0")
    selected_emoji_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_emojis.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    rating: Mapped[float]
    number_of_wins: Mapped[int]
    number_of_draws: Mapped[int]
    number_of_defeats: Mapped[int]
    game_location_game_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )

    emojis: Mapped[list[TableUserEmoji]] = relationship(
        lazy="selectin",
        foreign_keys=[TableUserEmoji.user_id],
    )
    stars_purchases: Mapped[list[TableStarsPurchase]] = relationship(
        lazy="selectin",
        foreign_keys=[TableStarsPurchase.user_id],
    )
    last_games: Mapped[list[TableLastGame]] = relationship(
        lazy="selectin",
        foreign_keys=[TableLastGame.user_id],
    )

    def entity(self) -> User:
        if self.game_location_game_id is not None:
            location = UserGameLocation(
                self.id,
                self.game_location_game_id,
            )
        else:
            location = None

        return User(
            id=self.id,
            account=Account(self.account_stars),
            emojis=[it.entity() for it in self.emojis],
            stars_purchases=[it.entity() for it in self.stars_purchases],
            last_games=[it.entity() for it in self.last_games],
            selected_emoji_id=self.selected_emoji_id,
            rating=self.rating,
            number_of_wins=self.number_of_wins,
            number_of_draws=self.number_of_draws,
            number_of_defeats=self.number_of_defeats,
            game_location=location,
        )

    @classmethod
    def of(cls, it: User) -> "TableUser":
        if it.game_location is None:
            game_location_game_id = None
        else:
            game_location_game_id = it.game_location.game_id

        return TableUser(
            id=it.id,
            account_stars=it.account.stars,
            selected_emoji_id=it.selected_emoji_id,
            rating_float=float(it.rating),
            number_of_wins=it.number_of_wins,
            number_of_draws=it.number_of_draws,
            number_of_defeats=it.number_of_defeats,
            game_location_game_id=game_location_game_id,
        )


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
    def of(cls, it: Game) -> "TableGame":
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

        return TableGame(
            id=it.id,
            user1_id=player1_id,
            ai1_id=ai1_id,
            player1_emoji_str=it.player1_emoji.str_,
            user2_id=player2_id,
            ai2_id=ai2_id,
            player2_emoji_str=it.player2_emoji.str_,
            state=TableGameState.of(it.state),
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


type TableUserAtomic = (
    TableUser | TableUserEmoji | TableStarsPurchase | TableLastGame
)
type TableGameAtomic = TableGame | TableCell | TableAi
type TablePaymentAtomic = TablePayment

type TableAtomic = TableUserAtomic | TableGameAtomic | TablePaymentAtomic


def table_entity(entity: Atomic) -> TableAtomic:  # noqa: PLR0911
    match entity:
        case User():
            return TableUser.of(entity)
        case UserEmoji():
            return TableUserEmoji.of(entity)
        case StarsPurchase():
            return TableStarsPurchase.of(entity)
        case LastGame():
            return TableLastGame.of(entity)

        case Game():
            return TableGame.of(entity)
        case Cell():
            return TableCell.of(entity)
        case Ai():
            return TableAi.of(entity)

        case Payment():
            return TablePayment.of(entity)
