from dataclasses import dataclass
from uuid import UUID

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.player.ports.player_views import PlayerViews
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.player import Player
from ttt.entities.core.stars import Stars
from ttt.infrastructure.sqlalchemy.tables import TablePlayer, TablePlayerEmoji
from ttt.presentation.aiogram.common.messages import (
    help_message,
    need_to_start_message,
)
from ttt.presentation.aiogram.player.messages import (
    emoji_already_purchased_message,
    emoji_not_purchased_to_select_message,
    emoji_selected_message,
    emoji_was_purchased_message,
    invalid_emoji_message,
    not_enough_stars_to_buy_emoji_message,
    profile_message,
    selected_emoji_removed_message,
    stars_added_message,
    stars_will_be_added_message,
    wait_emoji_to_buy_message,
    wait_stars_to_start_stars_purshase_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsPlayerViews(PlayerViews):
    _bot: Bot
    _session: AsyncSession

    async def render_view_of_player_with_id(
        self,
        location: PlayerLocation,
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
                TablePlayerEmoji.id == TablePlayer.selected_emoji_id,
            )
            .where(TablePlayer.id == location.player_id)
        )
        emoji_stmt = (
            select(TablePlayerEmoji.emoji_str)
            .where(TablePlayerEmoji.player_id == location.player_id)
            .order_by(TablePlayerEmoji.datetime_of_purchase)
        )

        player_result = await self._session.execute(player_stmt)
        player_row = player_result.first()

        if player_row is None:
            await need_to_start_message(self._bot, location.chat_id)
            return

        emojis = await self._session.scalars(emoji_stmt)

        await profile_message(
            self._bot,
            location.chat_id,
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
        await help_message(self._bot, location.chat_id)

    async def render_player_is_not_registered_view(
        self, location: PlayerLocation,
    ) -> None:
        await need_to_start_message(self._bot, location.chat_id)

    async def render_player_already_registered_view(
        self, location: PlayerLocation,
    ) -> None:
        await help_message(self._bot, location.chat_id)

    async def render_wait_emoji_to_buy_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await wait_emoji_to_buy_message(self._bot, location.chat_id)

    async def render_not_enough_stars_to_buy_emoji_view(
        self, location: PlayerLocation, stars_to_become_enough: Stars, /,
    ) -> None:
        await not_enough_stars_to_buy_emoji_message(
            self._bot,
            location.chat_id,
            stars_to_become_enough,
        )

    async def render_emoji_already_purchased_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await emoji_already_purchased_message(self._bot, location.chat_id)

    async def render_emoji_was_purchased_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await emoji_was_purchased_message(self._bot, location.chat_id)

    async def render_invalid_emoji_to_buy_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await invalid_emoji_message(self._bot, location.chat_id)

    async def render_invalid_emoji_to_select_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await invalid_emoji_message(self._bot, location.chat_id)

    async def render_emoji_not_purchased_to_select_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await emoji_not_purchased_to_select_message(self._bot, location.chat_id)

    async def render_emoji_selected_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await emoji_selected_message(self._bot, location.chat_id)

    async def render_selected_emoji_removed_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await selected_emoji_removed_message(self._bot, location.chat_id)

    async def render_wait_stars_to_start_stars_purshase_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await wait_stars_to_start_stars_purshase_message(
            self._bot, location.chat_id,
        )

    async def render_non_exchangeable_rubles_for_stars_view(
        self, location: PlayerLocation, /,
    ) -> None:
        raise NotImplementedError

    async def render_stars_purchase_will_be_completed_view(
        self, location: PlayerLocation, /,
    ) -> None:
        await stars_will_be_added_message(self._bot, location.chat_id)

    async def render_completed_stars_purshase_view(
        self, player: Player, purshase_id: UUID, location: PlayerLocation, /,
    ) -> None:
        await stars_added_message(self._bot, location.chat_id)
