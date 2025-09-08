from collections import OrderedDict
from dataclasses import dataclass
from typing import cast
from uuid import UUID

from aiogram import Bot
from aiogram_dialog import ShowMode, StartMode
from sqlalchemy import exists, func, select, union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

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
from ttt.entities.core.user.admin_right import AdminRightViaAdminToken, AdminRightViaOtherAdmin
from ttt.entities.core.user.location import UserGameLocation
from ttt.entities.core.user.user import User, is_user_admin, is_user_in_game
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.sqlalchemy.stmts import (
    selected_user_emoji_str_from_postgres,
    user_emojis_from_postgres,
)
from ttt.infrastructure.sqlalchemy.tables.user import (
    TableAdminRight,
    TableUser,
    TableUserEmoji,
)
from ttt.presentation.aiogram.common.messages import (
    need_to_start_message,
)
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.admin_dialog.main_window import (
    AdminMainMenuView,
)
from ttt.presentation.aiogram_dialog.admin_dialog.other_user_profile_window import (  # noqa: E501
    OtherUserProfileView,
)
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
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
class AiogramCommonUserViews(CommonUserViews):
    _bot: Bot
    _session: AsyncSession
    _result_buffer: ResultBuffer
    _dialog_manager_for_user: DialogManagerForUser

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
            select(
                TableUser.game_location_game_id,
                TableUser.account_stars,
                TableUser.rating,
                has_user_emojis_stmt,
            )
            .where(TableUser.id == user_id)
        )
        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            raise ValueError

        game_location_game_id = row.game_location_game_id

        if game_location_game_id is None:
            game_location = None
        else:
            game_location = UserGameLocation(user_id, game_location_game_id)

        view = MainMenuView.of(
            is_user_in_game=is_user_in_game(game_location),
            has_user_emojis=row.has_user_emojis,
            stars=row.account_stars,
            rating=row.rating,
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
        user_stmt = (
            select(
                TableUser.admin_right,
                TableUser.admin_right_via_other_admin_admin_id,
            )
            .where(TableUser.id == user_id)
        )
        user_result = await self._session.execute(user_stmt)
        user_row = user_result.first()

        if user_row is None or user_row.admin_right is None:
            user_admin_right = None
        else:
            user_admin_right = user_row.admin_right.entity(
                user_row.admin_right_via_other_admin_admin_id,
            )

        admin_trees_stmt = (
            select(
                TableUser.id,
                TableUser.admin_right,
                TableUser.admin_right_via_other_admin_admin_id,
            )
            .where(TableUser.admin_right.is_not(None))
        )
        admin_trees_result = await self._session.execute(admin_trees_stmt)
        admin_trees_rows = admin_trees_result.all()
        admin_trees = OrderedDict[int, list[int]]()
        admin_set = set[int]()
        admins_authorized_via_admin_token_count = 0
        admins_authorized_via_other_admins_count = 0
        for (
            row_id, row_admin_right, row_admin_right_via_other_admin_admin_id,
        ) in admin_trees_rows:
            admin_set.add(row_id)

            match cast(TableAdminRight, row_admin_right):
                case TableAdminRight.via_admin_token:
                    admins_authorized_via_admin_token_count += 1
                    admin_trees.setdefault(row_id, list())
                case TableAdminRight.via_other_admin:
                    admins_authorized_via_other_admins_count += 1
                    childs = admin_trees.setdefault(
                        row_admin_right_via_other_admin_admin_id,
                        list(),
                    )
                    childs.append(row_id)

        self._result_buffer.result = AdminMainMenuView.of(
            user_id,
            user_admin_right,
            admin_trees,
            admin_set,
            admins_authorized_via_admin_token_count,
            admins_authorized_via_other_admins_count,
        )

    async def user_authorized_as_admin_view(
        self,
        user: User,
        /,
    ) -> None:
        ...

    async def user_already_admin_to_get_admin_rights_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
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
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Админ-токен не верен"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def not_admin_to_relinquish_admin_right_view(
        self,
        user: User,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Вы уже не админ"},
            StartMode.RESET_STACK,
        )

    async def user_relinquished_admin_rights_view(self, user: User, /) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.main,
            {"hint": "🧿 Вы больше не админ"},
            StartMode.RESET_STACK,
        )

    async def user_is_not_admin_view(self, user: User, /) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.main,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND,
        )

    async def other_user_view(self, user: User, other_user_id: int, /) -> None:
        stmt = (
            select(
                TableUser.number_of_wins,
                TableUser.number_of_draws,
                TableUser.number_of_defeats,
                TableUser.account_stars,
                TableUser.rating,
                TableUser.admin_right,
                TableUser.admin_right_via_other_admin_admin_id,
            )
            .where(TableUser.id == other_user_id)
        )
        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            manager = self._dialog_manager_for_user(user.id)
            await manager.start(
                AdminDialogState.other_user_profile,
                {"hint": "🎭 Пользователь с таким ID не зарегестрирован:"},
                StartMode.RESET_STACK,
                ShowMode.DELETE_AND_SEND,
            )
            return

        if row.admin_right is None:
            admin_right = None
        else:
            admin_right = row.admin_right.entity(
                row.admin_right_via_other_admin_admin_id,
            )

        view = OtherUserProfileView.of(
            other_user_id,
            admin_right,
            row.number_of_wins,
            row.number_of_draws,
            row.number_of_defeats,
            row.account_stars,
            row.rating,
        )

        manager = self._dialog_manager_for_user(user.id)
        start_data = view.window_data()
        await manager.start(
            AdminDialogState.other_user_profile,
            start_data,
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def not_authorized_as_admin_via_admin_token_to_authorize_other_user_as_admin_view(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.authorize_other_user_as_admin,
            {"hint": "❌ Вы не авторизованы через админ-токен"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def other_user_already_admin_to_authorize_other_user_as_admin_view(
        self, user: User, other_user: User | None, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.authorize_other_user_as_admin,
            {"hint": "🧿 Пользователь уже админ"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def user_authorized_other_user_as_admin_view(
        self, user: User, other_user: User | None, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.authorize_other_user_as_admin,
            {"hint": "🧿 Права выданы"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def not_authorized_as_admin_via_admin_token_to_deauthorize_other_user_as_admin_view(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.deauthorize_other_user_as_admin,
            {"hint": "🧿 Вы не авторизованы через админ-токен"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize_view(
        self, user: User, other_user: User | None, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        hint = (
            "🧿 Пользователь должен быть авторизован как админ другим админом"
        )
        await manager.start(
            AdminDialogState.deauthorize_other_user_as_admin,
            {"hint": hint},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def user_deauthorized_other_user_as_admin_view(
        self, user: User, other_user: User | None, /,
    ) -> None:
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            AdminDialogState.deauthorize_other_user_as_admin,
            {"hint": "🧿 Пользователь больше не админ"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )


@dataclass(frozen=True, unsafe_hash=False)
class AiogramStarsPurchaseUserViews(StarsPurchaseUserViews):
    _dialog_manager_for_user: DialogManagerForUser

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
        manager = self._dialog_manager_for_user(user_id)
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
        manager = self._dialog_manager_for_user(user.id)
        await manager.start(
            MainDialogState.stars_shop,
            {"hint": "🌟 Звезды начислились!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )


@dataclass(frozen=True, unsafe_hash=False)
class AiogramEmojiSelectionUserViews(EmojiSelectionUserViews):
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
class AiogramEmojiPurchaseUserViews(EmojiPurchaseUserViews):
    _dialog_manager_for_user: DialogManagerForUser

    async def not_enough_stars_to_buy_emoji_view(
        self,
        user_id: int,
        stars_to_become_enough: Stars,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": f"😞 Нужно ещё {stars_to_become_enough} 🌟 для покупки"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def emoji_already_purchased_view(self, user_id: int, /) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": "🎭 Эмоджи уже куплен"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def emoji_was_purchased_view(self, user_id: int, /) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": "🌟 Куплено!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def invalid_emoji_to_buy_view(self, user_id: int, /) -> None:
        manager = self._dialog_manager_for_user(user_id)
        message_text = (
            "❌ Эмоджи должен состоять из одного символа"
        )
        await manager.start(
            MainDialogState.emoji_shop,
            {"hint": message_text},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
