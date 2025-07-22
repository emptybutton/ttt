from dataclasses import dataclass
from uuid import UUID

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.emoji_purchase.ports.user_views import (
    EmojiPurchaseUserViews,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)
from ttt.application.user.stars_purchase.ports.user_views import (
    StarsPurchaseUserViews,
)
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User
from ttt.infrastructure.sqlalchemy.tables import TableUser, TableUserEmoji
from ttt.presentation.aiogram.common.messages import (
    help_message,
    need_to_start_message,
)
from ttt.presentation.aiogram.user.messages import (
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
    wait_emoji_message,
    wait_stars_to_start_stars_purshase_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsCommonUserViews(CommonUserViews):
    _bot: Bot
    _session: AsyncSession

    async def render_view_of_user_with_id(
        self,
        location: UserLocation,
        /,
    ) -> None:
        user_stmt = (
            select(
                TableUser.number_of_wins,
                TableUser.number_of_draws,
                TableUser.number_of_defeats,
                TableUser.account_stars,
                TableUserEmoji.emoji_str.label("selected_emoji_str"),
                TableUser.game_location_game_id.is_not(None).label(
                    "is_in_game",
                ),
            )
            .outerjoin(
                TableUserEmoji,
                TableUserEmoji.id == TableUser.selected_emoji_id,
            )
            .where(TableUser.id == location.user_id)
        )
        emoji_stmt = (
            select(TableUserEmoji.emoji_str)
            .where(TableUserEmoji.player_id == location.user_id)
            .order_by(TableUserEmoji.datetime_of_purchase)
        )

        user_result = await self._session.execute(user_stmt)
        user_row = user_result.first()

        if user_row is None:
            await need_to_start_message(self._bot, location.chat_id)
            return

        emojis = await self._session.scalars(emoji_stmt)

        await profile_message(
            self._bot,
            location.chat_id,
            user_row.account_stars,
            tuple(emojis),
            user_row.selected_emoji_str,
            user_row.number_of_wins,
            user_row.number_of_draws,
            user_row.number_of_defeats,
            user_row.is_in_game,
        )

    async def render_user_registered_view(
        self,
        location: UserLocation,
    ) -> None:
        await help_message(self._bot, location.chat_id)

    async def render_user_is_not_registered_view(
        self,
        location: UserLocation,
    ) -> None:
        await need_to_start_message(self._bot, location.chat_id)

    async def render_user_already_registered_view(
        self,
        location: UserLocation,
    ) -> None:
        await help_message(self._bot, location.chat_id)

    async def render_selected_emoji_removed_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await selected_emoji_removed_message(self._bot, location.chat_id)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsStarsPurchaseUserViews(StarsPurchaseUserViews):
    _bot: Bot

    async def render_wait_stars_to_start_stars_purshase_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await wait_stars_to_start_stars_purshase_message(
            self._bot,
            location.chat_id,
        )

    async def render_invalid_stars_for_stars_purchase_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        raise NotImplementedError

    async def render_stars_purchase_will_be_completed_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await stars_will_be_added_message(self._bot, location.chat_id)

    async def render_completed_stars_purshase_view(
        self,
        user: User,
        purshase_id: UUID,
        location: UserLocation,
        /,
    ) -> None:
        await stars_added_message(self._bot, location.chat_id)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsEmojiSelectionUserViews(EmojiSelectionUserViews):
    _bot: Bot

    async def render_invalid_emoji_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await invalid_emoji_message(self._bot, location.chat_id)

    async def render_emoji_not_purchased_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await emoji_not_purchased_to_select_message(self._bot, location.chat_id)

    async def render_emoji_selected_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await emoji_selected_message(self._bot, location.chat_id)

    async def render_wait_emoji_to_select_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await wait_emoji_message(self._bot, location.chat_id)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsEmojiPurchaseUserViews(EmojiPurchaseUserViews):
    _bot: Bot

    async def render_wait_emoji_to_buy_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await wait_emoji_message(self._bot, location.chat_id)

    async def render_not_enough_stars_to_buy_emoji_view(
        self,
        location: UserLocation,
        stars_to_become_enough: Stars,
        /,
    ) -> None:
        await not_enough_stars_to_buy_emoji_message(
            self._bot,
            location.chat_id,
            stars_to_become_enough,
        )

    async def render_emoji_already_purchased_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await emoji_already_purchased_message(self._bot, location.chat_id)

    async def render_emoji_was_purchased_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await emoji_was_purchased_message(self._bot, location.chat_id)

    async def render_invalid_emoji_to_buy_view(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await invalid_emoji_message(self._bot, location.chat_id)
