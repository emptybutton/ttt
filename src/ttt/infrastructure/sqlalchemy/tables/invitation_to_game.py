from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
    InvitationToGameAtomic,
    InvitationToGameState,
)
from ttt.infrastructure.sqlalchemy.tables.common import Base
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


class TableInvitationToGameState(StrEnum):
    active = "active"
    auto_cancelled = "auto_cancelled"
    cancelled_by_user = "cancelled_by_user"
    rejected = "rejected"
    accepted = "accepted"

    def entity(self) -> InvitationToGameState:
        match self:
            case TableInvitationToGameState.active:
                return InvitationToGameState.active

            case TableInvitationToGameState.auto_cancelled:
                return InvitationToGameState.auto_cancelled

            case TableInvitationToGameState.cancelled_by_user:
                return InvitationToGameState.cancelled_by_user

            case TableInvitationToGameState.rejected:
                return InvitationToGameState.rejected

            case TableInvitationToGameState.accepted:
                return InvitationToGameState.accepted

    @classmethod
    def of(cls, it: InvitationToGameState) -> "TableInvitationToGameState":
        match it:
            case InvitationToGameState.active:
                return TableInvitationToGameState.active

            case InvitationToGameState.auto_cancelled:
                return TableInvitationToGameState.auto_cancelled

            case InvitationToGameState.cancelled_by_user:
                return TableInvitationToGameState.cancelled_by_user

            case InvitationToGameState.rejected:
                return TableInvitationToGameState.rejected

            case InvitationToGameState.accepted:
                return TableInvitationToGameState.accepted


invitation_to_game_state = postgresql.ENUM(
    TableInvitationToGameState, name="invitation_to_game_state",
)


class TableInvitationToGame(Base[InvitationToGame]):
    __tablename__ = "invitations_to_game"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    inviting_user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            deferrable=True,
            initially="DEFERRED",
        ),
        index=True,
    )
    invited_user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            deferrable=True,
            initially="DEFERRED",
        ),
        index=True,
    )
    invitation_datetime: Mapped[datetime]
    state: Mapped[TableInvitationToGameState] = mapped_column(
        invitation_to_game_state,
    )

    inviting_user: Mapped[TableUser] = relationship(
        lazy="selectin", foreign_keys=[inviting_user_id],
    )
    invited_user: Mapped[TableUser] = relationship(
        lazy="selectin", foreign_keys=[invited_user_id],
    )

    __table_args__ = (
        Index(
            "ix_invitations_to_game_user_ids",
            inviting_user_id,
            invited_user_id,
            postgresql_where=(state == TableInvitationToGameState.active.value),
            unique=True,
        ),
    )

    def __entity__(self) -> InvitationToGame:
        return InvitationToGame(
            id_=self.id,
            inviting_user=self.inviting_user.entity(),
            invited_user=self.invited_user.entity(),
            invitation_datetime=self.invitation_datetime,
            state=self.state.entity(),
        )

    @classmethod
    def of(cls, it: InvitationToGame) -> "TableInvitationToGame":
        return TableInvitationToGame(
            id=it.id_,
            inviting_user_id=it.inviting_user.id,
            invited_user_id=it.invited_user.id,
            invitation_datetime=it.invitation_datetime,
            state=TableInvitationToGameState.of(it.state),
        )


type TableInvitationToGameAtomic = TableInvitationToGame


def table_invitation_to_game_atomic(
    entity: InvitationToGameAtomic,
) -> TableInvitationToGameAtomic:
    match entity:
        case InvitationToGame():
            return TableInvitationToGame.of(entity)
