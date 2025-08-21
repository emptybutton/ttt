from dataclasses import dataclass
from uuid import UUID

from aiogram import Bot
from aiogram_dialog import BgManagerFactory, ShowMode, StartMode
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
from ttt.entities.core.user.user import User, is_user_admin, is_user_in_game
from ttt.infrastructure.sqlalchemy.stmts import (
    selected_user_emoji_str_from_postgres,
    user_emojis_from_postgres,
)
from ttt.infrastructure.sqlalchemy.tables.user import TableUser, TableUserEmoji
from ttt.presentation.aiogram.common.messages import (
    need_to_start_message,
)
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.admin_dialog.main_window import (
    AdminMainMenuView,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.emojis_window import (
    EmojiMenuView,
)
from ttt.presentation.aiogram_dialog.main_dialog.main_window import MainMenuView
from ttt.presentation.aiogram_dialog.main_dialog.profile_window import (
    UserProfileView,
)
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesFromPostgresAsCommonUserViews(CommonUserViews):
    _bot: Bot
    _session: AsyncSession
    _result_buffer: ResultBuffer
    _bg_dialog_manager_factory: BgManagerFactory

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

        view = UserProfileView.of(
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

        view = MainMenuView(
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

        self._result_buffer.result = (
            EmojiMenuView.of(emojis, selected_user_emoji_str)
        )

    async def user_is_not_registered_view(
        self,
        user_id: int,
    ) -> None:
        await need_to_start_message(self._bot, user_id)

    async def user_admin_view(self, user_id: int, /) -> None:
        stmt = select(TableUser.role).where(TableUser.id == user_id)
        table_role = await self._session.scalar(stmt)
        role = None if table_role is None else table_role.entity()

        self._result_buffer.result = (
            AdminMainMenuView(is_user_admin=is_user_admin(role))
        )

    async def user_got_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user.id, user.id,
        )
        await manager.update({}, ShowMode.DELETE_AND_SEND)

    async def user_already_admin_to_get_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user.id, user.id,
        )
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Вы уже админ"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def admin_token_mismatch_to_get_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user.id, user.id,
        )
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Админ-токен не верен"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def not_admin_to_relinquish_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user.id, user.id,
        )
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Вы уже не админ"},
            StartMode.RESET_STACK,
        )

    async def user_relinquished_admin_rights_view(self, user: User, /) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user.id, user.id,
        )
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Вы больше не админ"},
            StartMode.RESET_STACK,
        )


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsStarsPurchaseUserViews(StarsPurchaseUserViews):
    _bot: Bot
    _bg_dialog_manager_factory: BgManagerFactory

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
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await manager.start(
            MainDialogState.stars_shop,
            {"hint": "🌟 Звёзды скоро начислятся!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def completed_stars_purchase_view(
        self,
        user: User,
        purchase_id: UUID,
        /,
    ) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user.id, user.id,
        )
        await manager.start(
            MainDialogState.stars_shop,
            {"hint": "🌟 Звезды начислились!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )


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
        raise NotImplementedError

    async def emoji_not_purchased_to_select_view(
        self,
        user_id: int,
        /,
    ) -> None:
        raise NotImplementedError


@dataclass(frozen=True, unsafe_hash=False)
class AiogramMessagesAsEmojiPurchaseUserViews(EmojiPurchaseUserViews):
    _bot: Bot
    _bg_dialog_manager_factory: BgManagerFactory

    async def not_enough_stars_to_buy_emoji_view(
        self,
        user_id: int,
        stars_to_become_enough: Stars,
        /,
    ) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": f"😞 Нужно ещё {stars_to_become_enough} 🌟 для покупки"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def emoji_already_purchased_view(self, user_id: int, /) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": "🎭 Эмоджи уже куплен"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def emoji_was_purchased_view(self, user_id: int, /) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": "🌟 Куплено!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def invalid_emoji_to_buy_view(self, user_id: int, /) -> None:
        manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        message_text = (
            "❌ Эмоджи должен состоять из одного символа"
        )
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": message_text},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
