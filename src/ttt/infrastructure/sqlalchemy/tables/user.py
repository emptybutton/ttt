from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CHAR, BigInteger, ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.user.account import Account
from ttt.entities.core.user.admin_right import (
    AdminRight,
    AdminRightViaAdminToken,
    AdminRightViaOtherAdmin,
)
from ttt.entities.core.user.emoji import UserEmoji
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.user import User, UserAtomic
from ttt.entities.text.emoji import Emoji
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.sqlalchemy.tables.common import Base


class TableUserEmoji(Base[UserEmoji]):
    __tablename__ = "user_emojis"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    emoji_str: Mapped[str] = mapped_column(CHAR(1))
    datetime_of_purchase: Mapped[datetime]

    def __entity__(self) -> UserEmoji:
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


class TableAdminRight(StrEnum):
    via_admin_token = "via_admin_token"  # noqa: S105
    via_other_admin = "via_other_admin"

    def entity(
        self, admin_right_via_other_admin_admin_id: int | None,
    ) -> AdminRight:
        match self:
            case TableAdminRight.via_admin_token:
                return AdminRightViaAdminToken()
            case TableAdminRight.via_other_admin:
                return AdminRightViaOtherAdmin(
                    admin_id=not_none(admin_right_via_other_admin_admin_id),
                )


admin_right = postgresql.ENUM(TableAdminRight, name="admin_right")


class TableUser(Base[User]):
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
    admin_right: Mapped[TableAdminRight | None] = mapped_column(admin_right)
    admin_right_via_other_admin_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
    )

    emojis: Mapped[list[TableUserEmoji]] = relationship(
        lazy="selectin",
        foreign_keys=[TableUserEmoji.user_id],
    )

    __table_args__ = (
        Index(
            "ix_users_admin_right_via_other_admin_admin_id",
            admin_right_via_other_admin_admin_id,
            postgresql_where=(admin_right_via_other_admin_admin_id.is_not(None)),
        ),
        Index(
            "ix_users_admin_right",
            admin_right,
            postgresql_where=(admin_right.is_not(None)),
        ),
    )

    def __entity__(self) -> User:
        if self.game_location_game_id is not None:
            location = UserGameLocation(
                self.id,
                self.game_location_game_id,
            )
        else:
            location = None

        if self.admin_right is not None:
            admin_right = self.admin_right.entity(
                self.admin_right_via_other_admin_admin_id,
            )
        else:
            admin_right = None

        return User(
            id=self.id,
            account=Account(self.account_stars),
            emojis=[it.entity() for it in self.emojis],
            selected_emoji_id=self.selected_emoji_id,
            rating=self.rating,
            number_of_wins=self.number_of_wins,
            number_of_draws=self.number_of_draws,
            number_of_defeats=self.number_of_defeats,
            game_location=location,
            admin_right=admin_right,
        )

    @classmethod
    def of(cls, it: User) -> "TableUser":
        if it.game_location is None:
            game_location_game_id = None
        else:
            game_location_game_id = it.game_location.game_id

        match it.admin_right:
            case None:
                admin_right = None
                admin_right_via_other_admin_admin_id = None
            case AdminRightViaAdminToken():
                admin_right = TableAdminRight.via_admin_token
                admin_right_via_other_admin_admin_id = None
            case AdminRightViaOtherAdmin(admin_id):
                admin_right = TableAdminRight.via_other_admin
                admin_right_via_other_admin_admin_id = admin_id

        return TableUser(
            id=it.id,
            account_stars=it.account.stars,
            selected_emoji_id=it.selected_emoji_id,
            rating=it.rating,
            number_of_wins=it.number_of_wins,
            number_of_draws=it.number_of_draws,
            number_of_defeats=it.number_of_defeats,
            game_location_game_id=game_location_game_id,
            admin_right=admin_right,
            admin_right_via_other_admin_admin_id=(
                admin_right_via_other_admin_admin_id
            ),
        )


type TableUserAtomic = TableUser | TableUserEmoji


def table_user_atomic(entity: UserAtomic) -> TableUserAtomic:
    match entity:
        case User():
            return TableUser.of(entity)
        case UserEmoji():
            return TableUserEmoji.of(entity)
