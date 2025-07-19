from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CHAR, BigInteger, ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ttt.entities.atomic import Atomic
from ttt.entities.core.game.ai import Ai, AiType
from ttt.entities.core.game.board import Board
from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import (
    Game,
    GameCancellationResult,
    GameCompletionResult,
    GameResult,
    GameState,
    number_of_unfilled_cells,
)
from ttt.entities.core.game.player import Player
from ttt.entities.core.game.win import AiWin, Win
from ttt.entities.core.user.account import Account
from ttt.entities.core.user.emoji import UserEmoji
from ttt.entities.core.user.location import UserGameLocation, UserLocation
from ttt.entities.core.user.stars_purchase import StarsPurchase
from ttt.entities.core.user.user import User
from ttt.entities.core.user.win import UserWin
from ttt.entities.finance.payment.payment import Payment, PaymentState
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.finance.rubles import Rubles
from ttt.entities.math.matrix import Matrix
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import not_none


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
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    emoji_str: Mapped[str] = mapped_column(CHAR(1))
    datetime_of_purchase: Mapped[datetime]

    def entity(self) -> UserEmoji:
        return UserEmoji(
            self.id,
            self.player_id,
            Emoji(self.emoji_str),
            self.datetime_of_purchase,
        )

    @classmethod
    def of(cls, it: UserEmoji) -> "TableUserEmoji":
        return TableUserEmoji(
            id=it.id,
            player_id=it.user_id,
            emoji_str=it.emoji.str_,
            datetime_of_purchase=it.datetime_of_purchase,
        )


class TableStarsPurchase(Base):
    __tablename__ = "stars_purchases"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    location_player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    location_chat_id: Mapped[int] = mapped_column(BigInteger())
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
            location=UserLocation(
                self.location_player_id,
                self.location_chat_id,
            ),
            stars=self.stars,
            payment=None if self.payment is None else self.payment.entity(),
        )

    @classmethod
    def of(cls, it: StarsPurchase) -> "TableStarsPurchase":
        return TableStarsPurchase(
            id=it.id_,
            location_player_id=it.location.user_id,
            location_chat_id=it.location.chat_id,
            stars=it.stars,
            payment_id=None if it.payment is None else it.payment.id_,
        )


class TableUser(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    account_stars: Mapped[int] = mapped_column(server_default="0")
    selected_emoji_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_emojis.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    number_of_wins: Mapped[int]
    number_of_draws: Mapped[int]
    number_of_defeats: Mapped[int]
    game_location_game_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    game_location_chat_id: Mapped[int | None] = mapped_column(BigInteger())

    emojis: Mapped[list[TableUserEmoji]] = relationship(
        lazy="selectin",
        foreign_keys=[TableUserEmoji.player_id],
    )
    stars_purchases: Mapped[list[TableStarsPurchase]] = relationship(
        lazy="selectin",
        foreign_keys=[TableStarsPurchase.location_player_id],
    )

    def entity(self) -> User:
        if (
            self.game_location_game_id is not None
            and self.game_location_chat_id is not None
        ):
            location = UserGameLocation(
                self.id,
                self.game_location_chat_id,
                self.game_location_game_id,
            )
        else:
            location = None

        return User(
            self.id,
            Account(self.account_stars),
            [it.entity() for it in self.emojis],
            [it.entity() for it in self.stars_purchases],
            self.selected_emoji_id,
            self.number_of_wins,
            self.number_of_draws,
            self.number_of_defeats,
            location,
        )

    @classmethod
    def of(cls, it: User) -> "TableUser":
        if it.game_location is None:
            game_location_game_id = None
            game_location_chat_id = None
        else:
            game_location_game_id = it.game_location.game_id
            game_location_chat_id = it.game_location.chat_id

        return TableUser(
            id=it.id,
            account_stars=it.account.stars,
            selected_emoji_id=it.selected_emoji_id,
            number_of_wins=it.number_of_wins,
            number_of_draws=it.number_of_draws,
            number_of_defeats=it.number_of_defeats,
            game_location_game_id=game_location_game_id,
            game_location_chat_id=game_location_chat_id,
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


class TableGameResultType(StrEnum):
    completed = "completed"
    cancelled = "cancelled"


game_result_type = postgresql.ENUM(TableGameResultType, name="game_result_type")


class TableGameResult(Base):
    __tablename__ = "game_results"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
        unique=True,
    )
    type: Mapped[TableGameResultType] = mapped_column(game_result_type)

    win_winner_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    win_new_stars: Mapped[int | None]

    ai_win_ai_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ais.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )

    canceler_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )

    def entity(self) -> GameResult:
        win: Win | None

        if self.ai_win_ai_id is not None:
            win = AiWin(self.ai_win_ai_id)
        elif self.win_winner_id is None:
            win = None
        else:
            win = UserWin(self.win_winner_id, self.win_new_stars)

        match self.type:
            case TableGameResultType.completed:
                return GameCompletionResult(
                    self.id,
                    self.game_id,
                    win,
                )
            case TableGameResultType.cancelled:
                return GameCancellationResult(
                    self.id,
                    self.game_id,
                    not_none(self.canceler_id),
                )

    @classmethod
    def of(cls, it: GameResult) -> "TableGameResult":
        match it:
            case GameCompletionResult():
                if it.win is None:
                    win_winner_id = None
                    win_new_stars = None
                    ai_win_ai_id = None
                elif isinstance(it.win, UserWin):
                    win_winner_id = it.win.user_id
                    win_new_stars = it.win.new_stars
                    ai_win_ai_id = None
                else:
                    win_winner_id = None
                    win_new_stars = None
                    ai_win_ai_id = it.win.ai_id

                return TableGameResult(
                    id=it.id,
                    game_id=it.game_id,
                    type=TableGameResultType.completed,
                    win_winner_id=win_winner_id,
                    win_new_stars=win_new_stars,
                    ai_win_ai_id=ai_win_ai_id,
                    canceler_id=None,
                )

            case GameCancellationResult():
                return TableGameResult(
                    id=it.id,
                    game_id=it.game_id,
                    type=TableGameResultType.cancelled,
                    win_winner_id=None,
                    win_new_stars=None,
                    ai_win_ai_id=None,
                    canceler_id=it.canceler_id,
                )


class TableCell(Base):
    __tablename__ = "cells"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    game_id: Mapped[UUID] = mapped_column(
        ForeignKey("games.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    board_position_x: Mapped[int]
    board_position_y: Mapped[int]
    filler_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
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
            self.filler_id,
            self.ai_filler_id,
        )

    @classmethod
    def of(cls, it: Cell) -> "TableCell":
        return TableCell(
            id=it.id,
            game_id=it.game_id,
            board_position_x=it.board_position[0],
            board_position_y=it.board_position[1],
            filler_id=it.user_filler_id,
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
    player1_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    player2_id: Mapped[int | None] = mapped_column(
        BigInteger(),
        ForeignKey("players.id", deferrable=True, initially="DEFERRED"),
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

    result: Mapped["TableGameResult | None"] = relationship(lazy="joined")
    player1: Mapped["TableUser | None"] = relationship(
        lazy="joined",
        foreign_keys=[player1_id],
    )
    player2: Mapped["TableUser | None"] = relationship(
        lazy="joined",
        foreign_keys=[player2_id],
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

    def entity(self) -> Game:
        board = self._board(it.entity() for it in self.cells)

        player1: Player

        if self.player1 is not None:
            player1 = self.player1.entity()
        elif self.ai1 is not None:
            player1 = self.ai1.entity()
        else:
            raise ValueError

        player2: Player

        if self.player2 is not None:
            player2 = self.player2.entity()
        elif self.ai2 is not None:
            player2 = self.ai2.entity()
        else:
            raise ValueError

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
            player1_id=player1_id,
            ai1_id=ai1_id,
            player1_emoji_str=it.player1_emoji.str_,
            player2_id=player2_id,
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


type TableUserAtomic = TableUser | TableUserEmoji | TableStarsPurchase
type TableGameAtomic = TableGame | TableGameResult | TableCell | TableAi
type TablePaymentAtomic = TablePayment

type TableAtomic = (
    TableUserAtomic
    | TableGameAtomic
    | TablePaymentAtomic
)


def table_entity(entity: Atomic) -> TableAtomic:  # noqa: PLR0911
    match entity:
        case User():
            return TableUser.of(entity)
        case UserEmoji():
            return TableUserEmoji.of(entity)
        case StarsPurchase():
            return TableStarsPurchase.of(entity)

        case Game():
            return TableGame.of(entity)
        case GameCancellationResult() | GameCompletionResult():
            return TableGameResult.of(entity)
        case Cell():
            return TableCell.of(entity)
        case Ai():
            return TableAi.of(entity)

        case Payment():
            return TablePayment.of(entity)
