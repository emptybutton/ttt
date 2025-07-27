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
    wait_stars_to_start_stars_purchase_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsCommonUserViews(CommonUserViews):
    _bot: Bot
    _session: AsyncSession

    async def view_of_user_with_id(
        self,
        user_id: int,
        /,
    ) -> None:
        user_stmt = (
            select(
                TableUser.number_of_wins,
                TableUser.number_of_draws,
                TableUser.number_of_defeats,
                TableUser.account_stars,
                TableUser.rating,
                TableUserEmoji.emoji_str.label("selected_emoji_str"),
                TableUser.game_location_game_id.is_not(None).label(
                    "is_in_game",
                ),
            )
            .outerjoin(
                TableUserEmoji,
                TableUserEmoji.id == TableUser.selected_emoji_id,
            )
            .where(TableUser.id == user_id)
        )
        emoji_stmt = (
            select(TableUserEmoji.emoji_str)
            .where(TableUserEmoji.user_id == user_id)
            .order_by(TableUserEmoji.datetime_of_purchase)
        )

        user_result = await self._session.execute(user_stmt)
        user_row = user_result.first()

        if user_row is None:
            await need_to_start_message(self._bot, user_id)
            return

        emojis = await self._session.scalars(emoji_stmt)

        await profile_message(
            self._bot,
            user_id,
            user_row.account_stars,
            user_row.rating,
            tuple(emojis),
            user_row.selected_emoji_str,
            user_row.number_of_wins,
            user_row.number_of_draws,
            user_row.number_of_defeats,
            user_row.is_in_game,
        )

    async def user_registered_view(
        self,
        user_id: int,
    ) -> None:
        await help_message(self._bot, user_id)

    async def user_is_not_registered_view(
        self,
        user_id: int,
    ) -> None:
        await need_to_start_message(self._bot, user_id)

    async def user_already_registered_view(
        self,
        user_id: int,
    ) -> None:
        await help_message(self._bot, user_id)

    async def selected_emoji_removed_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await selected_emoji_removed_message(self._bot, user_id)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsStarsPurchaseUserViews(StarsPurchaseUserViews):
    _bot: Bot

    async def wait_stars_to_start_stars_purchase_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await wait_stars_to_start_stars_purchase_message(
            self._bot,
            user_id,
        )

    async def invalid_stars_for_stars_purchase_view(
        self,
        user_id: int,
        /,
    ) -> None:
        raise NotImplementedError

    async def stars_purchase_will_be_completed_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await stars_will_be_added_message(self._bot, user_id)

    async def completed_stars_purchase_view(
        self,
        user: User,
        purchase_id: UUID,
        /,
    ) -> None:
        await stars_added_message(self._bot, user.id)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsEmojiSelectionUserViews(EmojiSelectionUserViews):
    _bot: Bot

    async def invalid_emoji_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await invalid_emoji_message(self._bot, user_id)

    async def emoji_not_purchased_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await emoji_not_purchased_to_select_message(self._bot, user_id)

    async def emoji_selected_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await emoji_selected_message(self._bot, user_id)

    async def wait_emoji_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await wait_emoji_message(self._bot, user_id)


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsEmojiPurchaseUserViews(EmojiPurchaseUserViews):
    _bot: Bot

    async def wait_emoji_to_buy_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await wait_emoji_message(self._bot, user_id)

    async def not_enough_stars_to_buy_emoji_view(
        self,
        user_id: int,
        stars_to_become_enough: Stars,
        /,
    ) -> None:
        await not_enough_stars_to_buy_emoji_message(
            self._bot,
            user_id,
            stars_to_become_enough,
        )

    async def emoji_already_purchased_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await emoji_already_purchased_message(self._bot, user_id)

    async def emoji_was_purchased_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await emoji_was_purchased_message(self._bot, user_id)

    async def invalid_emoji_to_buy_view(
        self,
        user_id: int,
        /,
    ) -> None:
        await invalid_emoji_message(self._bot, user_id)
