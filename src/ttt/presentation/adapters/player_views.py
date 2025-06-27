from asyncio import gather
from dataclasses import dataclass

from aiogram.types.message import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.player.ports.player_views import PlayerViews
from ttt.entities.core.player.location import PlayerLocation
from ttt.infrastructure.sqlalchemy.tables import TablePlayer, TablePlayerEmoji
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
        player_stmt = (
            select(
                TablePlayer.number_of_wins,
                TablePlayer.number_of_draws,
                TablePlayer.number_of_defeats,
                TablePlayer.account_stars,
                TablePlayerEmoji.emoji_str.label("selected_emoji_str"),
                TablePlayer.game_location_game_id.is_not(None).label(
                    "is_in_game",
                ),
            )
            .outerjoin(
                TablePlayerEmoji,
                (TablePlayer.id == player_id)
                & (TablePlayerEmoji.id == TablePlayer.selected_emoji_id),
            )
        )
        emoji_stmt = (
            select(TablePlayerEmoji.emoji_str)
            .where(TablePlayerEmoji.player_id == player_id)
            .order_by(TablePlayerEmoji.datetime_of_purchase)
        )

        player_result, emojis = await gather(
            self._session.execute(player_stmt),
            self._session.scalars(emoji_stmt),
        )

        player_row = player_result.first()

        if player_row is None:
            await need_to_start_message(self._message)
            return

        await profile_message(
            self._message,
            player_row.account_stars,
            tuple(emojis),
            player_row.selected_emoji_str,
            player_row.number_of_wins,
            player_row.number_of_draws,
            player_row.number_of_defeats,
            player_row.is_in_game,
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
