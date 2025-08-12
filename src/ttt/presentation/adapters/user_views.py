from dataclasses import dataclass
from uuid import UUID

from aiogram import Bot
from sqlalchemy import exists, select
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
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.user import User, is_user_in_game
from ttt.infrastructure.sqlalchemy.stmts import (
    selected_user_emoji_str_from_postgres,
    user_emojis_from_postgres,
    user_exists_in_postgres,
)
from ttt.infrastructure.sqlalchemy.tables.user import TableUser, TableUserEmoji
from ttt.presentation.aiogram.common.dialogs import (
    EmojiListView,
    EmojiView,
    MainMenuCommonView,
    UserProfileView,
)
from ttt.presentation.aiogram.common.messages import (
    need_to_start_message,
)
from ttt.presentation.aiogram.common.texts import short_float_text
from ttt.presentation.aiogram.user.messages import (
    emoji_already_purchased_message,
    emoji_list_message,
    emoji_menu_message,
    emoji_not_purchased_to_select_message,
    emoji_was_purchased_message,
    invalid_emoji_message,
    menu_message,
    not_enough_stars_to_buy_emoji_message,
    stars_added_message,
    stars_will_be_added_message,
    wait_emoji_message,
    wait_stars_to_start_stars_purchase_message,
    welcome_message,
)
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsCommonUserViews(CommonUserViews):
    _bot: Bot
    _session: AsyncSession
    _result_buffer: ResultBuffer

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
            )
            .where(TableUser.id == user_id)
        )
        result = await self._session.execute(user_stmt)
        user_row = result.first()

        if user_row is None:
            await need_to_start_message(self._bot, user_id)
            return

        view = UserProfileView(
            user_row.number_of_wins,
            user_row.number_of_draws,
            user_row.number_of_defeats,
            user_row.account_stars,
            user_row.rating,
        )
        self._result_buffer.result = view

    async def user_menu_view(self, user_id: int, /) -> None:
        has_user_emojis_stmt = (
            exists(1).where(TableUserEmoji.user_id == user_id)
            .label("has_user_emojis")
        )
        stmt = (
            select(TableUser.game_location_game_id, has_user_emojis_stmt)
            .where(TableUser.id == user_id)
        )
        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            game_location_game_id = None
            has_user_emojis = False
        else:
            game_location_game_id = row.game_location_game_id
            has_user_emojis = row.has_user_emojis

        if game_location_game_id is None:
            game_location = None
        else:
            game_location = UserGameLocation(user_id, game_location_game_id)

        view = MainMenuCommonView(
            is_user_in_game(game_location), has_user_emojis,
        )
        self._result_buffer.result = view

    async def view_of_user_emojis_with_id(
        self,
        user_id: int,
        /,
    ) -> None:
        emojis = await user_emojis_from_postgres(self._session, user_id)
        selected_user_emoji_str = await selected_user_emoji_str_from_postgres(
            self._session, user_id,
        )
        emoji_views = tuple(
            EmojiView(emoji, is_emoji_selected=emoji == selected_user_emoji_str)
            for emoji in emojis
        )

        self._result_buffer.result = EmojiListView(
            emoji_views,
            is_any_emoji_selected=selected_user_emoji_str is not None,
        )

    async def user_registered_view(
        self,
        user: User,
    ) -> None:
        await welcome_message(self._bot, user.id, user.is_in_game())

    async def user_is_not_registered_view(
        self,
        user_id: int,
    ) -> None:
        await need_to_start_message(self._bot, user_id)

    async def user_already_registered_view(
        self,
        user: User,
    ) -> None:
        await welcome_message(self._bot, user.id, user.is_in_game())

    async def selected_emoji_removed_view(
        self,
        user_id: int,
        /,
    ) -> None:
        if not await user_exists_in_postgres(self._session, user_id):
            await need_to_start_message(self._bot, user_id)
            return

        emojis = await user_emojis_from_postgres(self._session, user_id)
        selected_user_emoji_str = await selected_user_emoji_str_from_postgres(
            self._session, user_id,
        )

        await emoji_menu_message(
            self._bot, user_id, emojis, selected_user_emoji_str,
        )

    async def menu_view(
        self,
        user_id: int,
        /,
    ) -> None:
        stmt = (
            select(TableUser.game_location_game_id.is_not(None))
            .where(TableUser.id == user_id)
        )
        is_user_in_game = await self._session.scalar(stmt)

        if is_user_in_game is None:
            await need_to_start_message(self._bot, user_id)
            return

        await menu_message(self._bot, user_id, is_user_in_game)

    async def emoji_menu_view(self, user_id: int, /) -> None:
        if not await user_exists_in_postgres(self._session, user_id):
            await need_to_start_message(self._bot, user_id)
            return

        emojis = await user_emojis_from_postgres(self._session, user_id)
        selected_user_emoji_str = await selected_user_emoji_str_from_postgres(
            self._session, user_id,
        )

        await emoji_menu_message(
            self._bot, user_id, emojis, selected_user_emoji_str,
        )


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
class AiogramMessagesFromPostgresAsEmojiSelectionUserViews(
    EmojiSelectionUserViews,
):
    _bot: Bot
    _session: AsyncSession

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
        if not await user_exists_in_postgres(self._session, user_id):
            await need_to_start_message(self._bot, user_id)
            return

        emojis = await user_emojis_from_postgres(self._session, user_id)
        selected_user_emoji_str = await selected_user_emoji_str_from_postgres(
            self._session, user_id,
        )

        await emoji_list_message(
            self._bot, user_id, emojis, selected_user_emoji_str,
        )

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
