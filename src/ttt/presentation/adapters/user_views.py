from asyncio import gather
from collections import OrderedDict
from dataclasses import dataclass
from typing import cast

from aiogram import Bot
from aiogram_dialog import ShowMode, StartMode
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.user.change_other_user_account.ports.user_views import (
    ChangeOtherUserAccountViews,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.emoji_purchase.ports.user_views import (
    EmojiPurchaseUserViews,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)
from ttt.application.user.game.ports.user_views import GameUserViews
from ttt.entities.core.game.game import Game
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.user import User, is_user_in_game, user_stars
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.sqlalchemy.stmts import (
    max_rating_and_users_with_max_rating_from_postgres,
    selected_user_emoji_str_from_postgres,
    user_emojis_from_postgres,
)
from ttt.infrastructure.sqlalchemy.tables.game import TableGame
from ttt.infrastructure.sqlalchemy.tables.invitation_to_game import (
    TableInvitationToGame,
    TableInvitationToGameState,
)
from ttt.infrastructure.sqlalchemy.tables.user import (
    TableAdminRight,
    TableUser,
    TableUserEmoji,
)
from ttt.presentation.aiogram.common.messages import (
    need_to_start_message,
)
from ttt.presentation.aiogram_dialog.admin_dialog.change_other_user_account2_window import (  # noqa: E501
    ChangeOtherUserAccount2View,
)
from ttt.presentation.aiogram_dialog.admin_dialog.common import (
    AdminDialogState,
    AdminRightName,
)
from ttt.presentation.aiogram_dialog.admin_dialog.main_window import (
    AdminMainMenuViewForAdmin,
    AdminMainMenuViewForNotAdmin,
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
from ttt.presentation.aiogram_dialog.main_dialog.game_start_window import (
    GameStartView,
)
from ttt.presentation.aiogram_dialog.main_dialog.game_window import (
    ActiveGameView,
)
from ttt.presentation.aiogram_dialog.main_dialog.main_window import (
    AmoutOfIncomingInvitationsToGame,
    MainMenuView,
)
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
            select(TableUser.account_stars, TableUser.rating)
            .where(TableUser.id == user_id)
        )
        result = await self._session.execute(user_stmt)
        user_row = result.first()

        if user_row is None:
            await need_to_start_message(self._bot, user_id)
            return

        wins_stmt = (
            select(func.count(1))
            .where(TableGame.result_decided_game_user_win_user_id == user_id)
        )
        wins = not_none(await self._session.scalar(wins_stmt))

        draws_stmt = (
            select(func.count(1))
            .where(
                (TableGame.result_draw_game_user_draw1_user_id == user_id)
                | (TableGame.result_draw_game_user_draw2_user_id == user_id),
            )
        )
        draws = not_none(await self._session.scalar(draws_stmt))

        defeats_stmt = (
            select(func.count(1))
            .where(TableGame.result_decided_game_user_loss_user_id == user_id)
        )
        defeats = not_none(await self._session.scalar(defeats_stmt))

        max_rating, users_with_max_rating = (
            await max_rating_and_users_with_max_rating_from_postgres(
                self._session,
            )
        )

        view = UserProfileView.of(
            wins,
            draws,
            defeats,
            user_row.account_stars,
            user_row.rating,
            max_rating,
            users_with_max_rating,
        )
        self._result_buffer.result = view

    async def user_menu_view(self, user_id: int, /) -> None:
        has_user_emojis_stmt = (
            exists(1).where(TableUserEmoji.user_id == user_id)
            .label("has_user_emojis")
        )
        stmt = (
            select(
                TableUser.current_game_id,
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

        incoming_invitations_to_game_stmt = (
            select(func.count(1))
            .where(
                (TableInvitationToGame.invited_user_id == user_id)
                & (
                    TableInvitationToGame.state
                    == TableInvitationToGameState.active.value
                ),
            )
            .limit(2)
        )
        incoming_invitations_to_game = await self._session.scalar(
            incoming_invitations_to_game_stmt,
        )

        amout_of_incoming_invitations_to_game: AmoutOfIncomingInvitationsToGame

        if (
            incoming_invitations_to_game == 0
            or incoming_invitations_to_game is None
        ):
            amout_of_incoming_invitations_to_game = "no"
        elif incoming_invitations_to_game == 1:
            amout_of_incoming_invitations_to_game = "one"
        else:
            amout_of_incoming_invitations_to_game = "many"

        max_rating, users_with_max_rating = (
            await max_rating_and_users_with_max_rating_from_postgres(
                self._session,
            )
        )
        view = MainMenuView(
            is_user_in_game=is_user_in_game(row.current_game_id),
            has_user_emojis=row.has_user_emojis,
            stars=row.account_stars,
            rating=row.rating,
            amout_of_incoming_invitations_to_game=(
                amout_of_incoming_invitations_to_game
            ),
            max_rating=max_rating,
            users_with_max_rating=users_with_max_rating,
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

    def _admin_right_name(
        self, table_admin_right: TableAdminRight,
    ) -> AdminRightName:
        match table_admin_right:
            case TableAdminRight.via_admin_token:
                return "via_admin_token"
            case TableAdminRight.via_other_admin:
                return "via_other_admin"

    async def user_admin_view(self, user_id: int, /) -> None:
        user_stmt = select(TableUser.admin_right).where(TableUser.id == user_id)
        user_table_admin_right = await self._session.scalar(user_stmt)

        if user_table_admin_right is None:
            self._result_buffer.result = AdminMainMenuViewForNotAdmin()
            return

        user_admin_right_name = self._admin_right_name(user_table_admin_right)

        admin_stmt = (
            select(
                TableUser.id,
                TableUser.admin_right,
                TableUser.admin_right_via_other_admin_admin_id,
            )
            .where(TableUser.admin_right.is_not(None))
        )
        admin_result = await self._session.execute(admin_stmt)
        admin_rows = admin_result.all()

        admin_tree_index = dict[int, list[int]]()
        admin_right_name_map = dict[int, AdminRightName]()
        admins_authorized_via_admin_token_count = 0
        admins_authorized_via_other_admins_count = 0

        for row in admin_rows:
            match cast(TableAdminRight, row.admin_right):
                case TableAdminRight.via_admin_token:
                    admins_authorized_via_admin_token_count += 1
                case TableAdminRight.via_other_admin:
                    admins_authorized_via_other_admins_count += 1

        for row in admin_rows:
            admin_right_name_map[row.id] = self._admin_right_name(
                row.admin_right,
            )

        for row in admin_rows:
            match cast(TableAdminRight, row.admin_right):
                case TableAdminRight.via_admin_token:
                    admin_tree_index.setdefault(row.id, list())
                case TableAdminRight.via_other_admin:
                    childs = admin_tree_index.setdefault(
                        row.admin_right_via_other_admin_admin_id, list(),
                    )
                    childs.append(row.id)

        admin_trees = OrderedDict(
            sorted(admin_tree_index.items(), key=lambda item: item[0]),
        )
        for childs in admin_trees.values():
            childs.sort()

        self._result_buffer.result = AdminMainMenuViewForAdmin.of(
            user_id,
            user_admin_right_name,
            admin_trees,
            admin_right_name_map,
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

        wins_stmt = select(func.count(1)).where(
            TableGame.result_decided_game_user_win_user_id == other_user_id,
        )
        wins = not_none(await self._session.scalar(wins_stmt))

        draws_stmt = select(func.count(1)).where(
            (TableGame.result_draw_game_user_draw1_user_id == other_user_id)
            | (TableGame.result_draw_game_user_draw2_user_id == other_user_id),
        )
        draws = not_none(await self._session.scalar(draws_stmt))

        defeats_stmt = select(func.count(1)).where(
            TableGame.result_decided_game_user_loss_user_id == other_user_id,
        )
        defeats = not_none(await self._session.scalar(defeats_stmt))

        if row.admin_right is None:
            admin_right = None
        else:
            admin_right = row.admin_right.entity(
                row.admin_right_via_other_admin_admin_id,
            )

        max_rating, users_with_max_rating = (
            await max_rating_and_users_with_max_rating_from_postgres(
                self._session,
            )
        )

        view = OtherUserProfileView.of(
            other_user_id,
            admin_right,
            wins,
            draws,
            defeats,
            row.account_stars,
            row.rating,
            max_rating,
            users_with_max_rating,
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

    async def other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize_view(  # noqa: E501
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


@dataclass(frozen=True, unsafe_hash=False)
class AiogramChangeOtherUserAccountViews(ChangeOtherUserAccountViews):
    _dialog_manager_for_user: DialogManagerForUser
    _session: AsyncSession
    _result_buffer: ResultBuffer

    async def user_account_to_change_view(
        self, user_id: int, other_user_id: int, /,
    ) -> None:
        stmt = (
            select(TableUser.account_stars)
            .where(TableUser.id == other_user_id)
        )
        stars = await self._session.scalar(stmt)
        stars = user_stars(stars)

        self._result_buffer.result = ChangeOtherUserAccount2View(stars)

    async def user_set_other_user_account_view(
        self, user: User, other_user: User, /,
    ) -> None:
        await self._account_view(
            user.id, other_user.id, other_user.account.stars,
        )

    async def user_changed_other_user_account_view(
        self,
        user: User,
        other_user: User,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None:
        await self._account_view(
            user.id, other_user.id, other_user.account.stars,
        )

    async def negative_account_on_change_other_user_account_view(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None:
        await self._negative_account_view(user.id, other_user_id)

    async def negative_account_on_set_other_user_account_view(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars: Stars,
        /,
    ) -> None:
        await self._negative_account_view(user.id, other_user_id)

    async def _negative_account_view(
        self, user_id: int, other_user_id: int,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        start_data = {
            "hint": "Счёт не может быть отрицательным 👎",
            "other_user_id": other_user_id,
        }
        await manager.start(
            AdminDialogState.change_other_user_account2,
            start_data,
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def _account_view(
        self, user_id: int, other_user_id: int, other_user_account_stars: Stars,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        start_data = {
            "other_user_id": other_user_id,
            "other_user_account_stars": other_user_account_stars,
        }
        await manager.start(
            AdminDialogState.change_other_user_account2,
            start_data,
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )


@dataclass(frozen=True, unsafe_hash=False)
class AiogramGameUserViews(GameUserViews):
    _dialog_manager_for_user: DialogManagerForUser
    _result_buffer: ResultBuffer
    _session: AsyncSession

    async def user_is_waiting_for_matchmaking_view(
        self,
        user: User,
        /,
    ) -> None:
        ...

    async def user_is_already_waiting_for_matchmaking_view(
        self,
        user: User,
        /,
    ) -> None:
        ...

    async def user_is_in_game_to_wait_for_matchmaking_view(
        self, user: User, /,
    ) -> None:
        dialog_manager = self._dialog_manager_for_user(user.id)
        await dialog_manager.start(
            MainDialogState.game_mode_to_start_game,
            {"hint": "⚔️ Вы уже в игре"},
            StartMode.RESET_STACK,
        )

    async def matched_games_view(self, games: list[Game], /) -> None:
        await gather(*map(self._started_game_view, games))

    async def _started_game_view(self, game: Game, /) -> None:
        await gather(*(
            self._started_game_view_for_user(user.id, game)
            for user in game.users()
        ))

    async def _started_game_view_for_user(
        self, user_id: int, game: Game, /,
    ) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)
        await dialog_manager.start(
            MainDialogState.game,
            ActiveGameView.of(game, user_id).window_data(),
            StartMode.RESET_STACK,
        )

    async def user_is_not_waiting_for_matchmaking_to_dont_wait_view(
        self, user: User, /,
    ) -> None:
        ...

    async def user_is_not_waiting_for_matchmaking_view(
        self, user: User, /,
    ) -> None:
        ...

    async def matchmaking_view(self, user_id: int, /) -> None:
        stmt = (
            select(TableUser.has_matchmaking_waiting)
            .where(TableUser.id == user_id)
        )
        has_matchmaking_waiting = await self._session.scalar(stmt)

        if has_matchmaking_waiting is None:
            self._result_buffer.result = None
        else:
            self._result_buffer.result = GameStartView(
                is_user_waiting_for_matchmaking=has_matchmaking_waiting,
            )
