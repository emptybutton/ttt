from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.invitation_to_game.game.ports.invitation_to_game_dao import (  # noqa: E501
    InvitationToGameDao,
)
from ttt.infrastructure.sqlalchemy.tables.invitation_to_game import (
    TableInvitationToGame,
    TableInvitationToGameState,
)


@dataclass(frozen=True, unsafe_hash=False)
class PostgresInvitationToGameDao(InvitationToGameDao):
    _session: AsyncSession

    async def set_auto_cancelled_where_invitation_datetime_le_and_active(
        self,
        datetime: datetime,
        /,
    ) -> Sequence[UUID]:
        stmt = (
            update(TableInvitationToGame)
            .values(state=TableInvitationToGameState.auto_cancelled.value)
            .where(
                (TableInvitationToGame.invitation_datetime <= datetime)
                & (
                    TableInvitationToGame.state
                    == TableInvitationToGameState.active.value
                ),
            )
            .returning(TableInvitationToGame.id)
        )
        result = await self._session.scalars(stmt)
        return result.all()
