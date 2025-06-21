from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any

from aiogram.types.message import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.player.ports.player_views import PlayerViews
from ttt.infrastructure.sqlalchemy.tables import TablePlayer
from ttt.presentation.aiogram.common.messages import need_to_start_message
from ttt.presentation.aiogram.player.messages import player_info_message


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsPlayerViews(PlayerViews[Awaitable[Any]]):
    _message: Message
    _session: AsyncSession

    async def view_of_player_with_id(
        self, player_id: int, /,
    ) -> Awaitable[Any]:
        stmt = select(
            TablePlayer.number_of_wins,
            TablePlayer.number_of_draws,
            TablePlayer.number_of_defeats,
            TablePlayer.game_location_game_id.is_not(None).label("is_in_game"),
        ).where(
            TablePlayer.id == player_id,
        ).limit(1)

        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            return need_to_start_message(self._message)

        return player_info_message(
            self._message,
            row.number_of_wins,
            row.number_of_draws,
            row.number_of_defeats,
            row.is_in_game,
        )
