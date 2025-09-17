from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.matchmaking.matchmaking import (
    Matchmaking,
    MatchmakingAtomic,
)
from ttt.entities.core.matchmaking.user_waiting import UserWaiting
from ttt.infrastructure.sqlalchemy.tables.common import Base
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


class TableUserWaiting(Base[UserWaiting]):
    __tablename__ = "matchmaking_user_waitings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    start_datetime: Mapped[datetime]
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            deferrable=True,
            initially="DEFERRED",
        ),
        index=True,
    )

    user: Mapped[TableUser] = relationship(lazy="selectin")

    def __entity__(self) -> UserWaiting:
        return UserWaiting(
            id_=self.id,
            user=self.user.entity(),
            start_datetime=self.start_datetime,
        )

    @classmethod
    def of(cls, it: UserWaiting) -> "TableUserWaiting":
        return TableUserWaiting(
            id=it.id_,
            user_id=it.user.id,
            start_datetime=it.start_datetime,
        )


type TableMatchmaking = None
type TableMatchmakingAtomic = TableMatchmaking | TableUserWaiting


def table_matchmaking_atomic(
    entity: MatchmakingAtomic,
) -> TableMatchmakingAtomic:
    match entity:
        case Matchmaking():
            return None

        case UserWaiting():
            return TableUserWaiting.of(entity)
