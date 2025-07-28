from datetime import datetime
from uuid import UUID

from sqlalchemy import CHAR, BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.user.account import Account
from ttt.entities.core.user.emoji import UserEmoji
from ttt.entities.core.user.last_game import LastGame
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.stars_purchase import StarsPurchase
from ttt.entities.core.user.user import User, UserAtomic
from ttt.entities.text.emoji import Emoji
from ttt.infrastructure.sqlalchemy.tables.common import Base
from ttt.infrastructure.sqlalchemy.tables.payment import TablePayment


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
            rating=it.rating,
            number_of_wins=it.number_of_wins,
            number_of_draws=it.number_of_draws,
            number_of_defeats=it.number_of_defeats,
            game_location_game_id=game_location_game_id,
        )


type TableUserAtomic = (
    TableUser | TableUserEmoji | TableStarsPurchase | TableLastGame
)


def table_user_atomic(entity: UserAtomic) -> TableUserAtomic:
    match entity:
        case User():
            return TableUser.of(entity)
        case UserEmoji():
            return TableUserEmoji.of(entity)
        case StarsPurchase():
            return TableStarsPurchase.of(entity)
        case LastGame():
            return TableLastGame.of(entity)
