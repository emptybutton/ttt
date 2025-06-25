from dataclasses import dataclass

from aiogram.types.message import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.player.ports.player_views import PlayerViews
from ttt.entities.core.player.location import PlayerLocation
from ttt.infrastructure.sqlalchemy.tables import TablePlayer
from ttt.presentation.aiogram.common.messages import (
    help_message,
    need_to_start_message,
)
from ttt.presentation.aiogram.player.messages import profile_message


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsPlayerViews(PlayerViews):
    _message: Message
    _session: AsyncSession

    async def render_view_of_player_with_id(
        self,
        player_id: int,
        /,
    ) -> None:
        stmt = (
            select(
                TablePlayer.number_of_wins,
                TablePlayer.number_of_draws,
                TablePlayer.number_of_defeats,
                TablePlayer.account_stars,
                TablePlayer.game_location_game_id.is_not(None).label(
                    "is_in_game",
                ),
            )
            .where(
                TablePlayer.id == player_id,
            )
            .limit(1)
        )

        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            await need_to_start_message(self._message)
            return

        await profile_message(
            self._message,
            row.account_stars,
            row.number_of_wins,
            row.number_of_draws,
            row.number_of_defeats,
            row.is_in_game,
        )

    async def render_player_registered_view(
        self, location: PlayerLocation,
    ) -> None:
        await help_message(self._message)

    async def render_player_is_not_registered_view(
        self, location: PlayerLocation,
    ) -> None:
        await need_to_start_message(self._message)

    async def render_player_already_registered_view(
        self, location: PlayerLocation,
    ) -> None:
        await help_message(self._message)
