from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.matchmaking_queue.matchmaking_queue import (
    MatchmakingQueue,
    MatchmakingQueueAtomic,
)
from ttt.entities.core.matchmaking_queue.user_waiting import UserWaiting
from ttt.infrastructure.sqlalchemy.tables.common import Base
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


class TableUserWaiting(Base):
    __tablename__ = "matchmaking_queue_user_waitings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    matchmaking_queue_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "matchmaking_queues.id",
            deferrable=True,
            initially="DEFERRED",
        ),
        index=True,
    )
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

    def entity(self) -> UserWaiting:
        return UserWaiting(
            id_=self.id,
            matchmaking_queue_id=self.matchmaking_queue_id,
            user=self.user.entity(),
            start_datetime=self.start_datetime,
        )

    @classmethod
    def of(cls, it: UserWaiting) -> "TableUserWaiting":
        return TableUserWaiting(
            id=it.id_,
            matchmaking_queue_id=it.matchmaking_queue_id,
            user_id=it.user.id,
            start_datetime=it.start_datetime,
        )


class TableMatchmakingQueue(Base):
    __tablename__ = "matchmaking_queues"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    user_waitings: Mapped[list[TableUserWaiting]] = relationship(
        lazy="selectin",
    )

    def entity(self) -> MatchmakingQueue:
        return MatchmakingQueue(
            id_=self.id,
            user_waitings=[it.entity() for it in self.user_waitings],
        )

    @classmethod
    def of(cls, it: MatchmakingQueue) -> "TableMatchmakingQueue":
        return TableMatchmakingQueue(
            id=it.id_,
        )


type TableMatchmakingQueueAtomic = TableMatchmakingQueue | TableUserWaiting


def table_matchmaking_queue_atomic(
    entity: MatchmakingQueueAtomic,
) -> TableMatchmakingQueueAtomic:
    match entity:
        case MatchmakingQueue():
            return TableMatchmakingQueue.of(entity)

        case UserWaiting():
            return TableUserWaiting.of(entity)
