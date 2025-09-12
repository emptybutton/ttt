from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.dialects.postgresql.base import (  # type: ignore[attr-defined]
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.invitation_to_game.game.ports.invitations_to_game import (
    InvitationsToGame,
)
from ttt.entities.core.invitation_to_game.invitation_to_game import (
    InvitationToGame,
)
from ttt.infrastructure.sqlalchemy.tables.invitation_to_game import (
    TableInvitationToGame,
)


@dataclass(frozen=True, unsafe_hash=False)
class InPostgresInvitationsToGame(InvitationsToGame):
    _session: AsyncSession

    async def invitation_to_game_with_id(
        self, id_: UUID, /,
    ) -> InvitationToGame | None:
        stmt = (
            select(TableInvitationToGame)
            .where(TableInvitationToGame.id == id_)
            .with_for_update()
        )
        table_invitation_to_game = await self._session.scalar(stmt)

        if table_invitation_to_game is None:
            return None

        return table_invitation_to_game.entity()
