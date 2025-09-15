from dataclasses import dataclass

from structlog.types import FilteringBoundLogger

from ttt.application.user.change_other_user_account.ports.user_log import (
    ChangeOtherUserAccountLog,
)
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.entities.core.stars import Stars
from ttt.entities.core.user.user import User
from ttt.entities.text.emoji import Emoji


@dataclass(frozen=True, unsafe_hash=False)
class StructlogCommonUserLog(CommonUserLog):
    _logger: FilteringBoundLogger

    async def user_registered(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_registered",
            user_id=user.id,
        )

    async def user_double_registration(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_double_registration",
            user_id=user.id,
        )

    async def user_viewed(self, user_id: int, /) -> None:
        await self._logger.ainfo(
            "user_viewed",
            user_id=user_id,
        )

    async def user_removed_emoji(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_removed_emoji",
            user_id=user.id,
        )

    async def menu_viewed(self, user_id: int) -> None:
        await self._logger.ainfo(
            "menu_viewed",
            user_id=user_id,
        )

    async def emoji_menu_viewed(self, user_id: int) -> None:
        await self._logger.ainfo(
            "emoji_menu_viewed",
            user_id=user_id,
        )

    async def user_authorized_as_admin(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_authorized_as_admin",
            user_id=user.id,
        )

    async def user_already_admin_to_get_admin_rights(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_already_admin_to_get_admin_rights",
            user_id=user.id,
        )

    async def admin_token_mismatch_to_get_admin_rights(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "admin_token_mismatch_to_get_admin_rights",
            user_id=user.id,
        )

    async def not_admin_to_relinquish_admin_right(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "not_admin_to_relinquish_admin_right",
            user_id=user.id,
        )

    async def user_relinquished_admin_rights(self, user: User, /) -> None:
        await self._logger.ainfo(
            "user_relinquished_admin_rights",
            user_id=user.id,
        )

    async def not_authorized_as_admin_via_admin_token_to_authorize_other_user_as_admin(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None:
        await self._logger.ainfo(
            "not_authorized_as_admin_via_admin_token_to_authorize_other_user_as_admin",
            user_id=user.id,
            other_user_id=None if other_user is None else other_user.id,
        )

    async def other_user_already_admin_to_authorize_other_user_as_admin(
        self, user: User, other_user: User | None, /,
    ) -> None:
        await self._logger.ainfo(
            "other_user_already_admin_to_authorize_other_user_as_admin",
            user_id=user.id,
            other_user_id=None if other_user is None else other_user.id,
        )

    async def user_authorized_other_user_as_admin(
        self, user: User, other_user: User | None, /,
    ) -> None:
        await self._logger.ainfo(
            "user_authorized_other_user_as_admin",
            user_id=user.id,
            other_user_id=None if other_user is None else other_user.id,
        )

    async def not_authorized_as_admin_via_admin_token_to_deauthorize_other_user_as_admin(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None:
        await self._logger.ainfo(
            "not_authorized_as_admin_via_admin_token_to_deauthorize_other_user_as_admin",
            user_id=user.id,
            other_user_id=None if other_user is None else other_user.id,
        )

    async def other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize(  # noqa: E501
        self, user: User, other_user: User | None, /,
    ) -> None:
        await self._logger.ainfo(
            "other_user_is_not_authorized_as_admin_via_other_admin_to_deauthorize",
            user_id=user.id,
            other_user_id=None if other_user is None else other_user.id,
        )

    async def user_deauthorized_other_user_as_admin(
        self, user: User, other_user: User | None, /,
    ) -> None:
        await self._logger.ainfo(
            "user_deauthorized_other_user_as_admin",
            user_id=user.id,
            other_user_id=None if other_user is None else other_user.id,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogEmojiPurchaseUserLog(EmojiPurchaseUserLog):
    _logger: FilteringBoundLogger

    async def user_bought_emoji(
        self,
        user: User,
        emoji: Emoji,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_bought_emoji",
            user_id=user.id,
            emoji=emoji.str_,
        )

    async def user_intends_to_buy_emoji(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_buy_emoji",
            user_id=user_id,
        )

    async def emoji_already_purchased_to_buy(
        self,
        user: User,
        emoji: Emoji,
    ) -> None:
        await self._logger.ainfo(
            "emoji_already_purchased_to_buy",
            user_id=user.id,
            emoji=emoji.str_,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogEmojiSelectionUserLog(EmojiSelectionUserLog):
    _logger: FilteringBoundLogger

    async def user_selected_emoji(
        self,
        user: User,
        emoji: Emoji,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_selected_emoji",
            user_id=user.id,
            emoji=emoji.str_,
        )

    async def user_intends_to_select_emoji(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_select_emoji",
            user_id=user_id,
        )

    async def emoji_not_purchased_to_select(
        self,
        user: User,
        emoji: Emoji,
    ) -> None:
        await self._logger.ainfo(
            "emoji_not_purchased_to_select",
            user_id=user.id,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogChangeOtherUserAccountLog(ChangeOtherUserAccountLog):
    _logger: FilteringBoundLogger

    async def user_is_not_admin_to_set_other_user_account(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars: Stars,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_is_not_admin_to_set_other_user_account",
            user_id=user.id,
            other_user_id=other_user_id,
            other_user_account_stars=other_user_account_stars,
        )

    async def user_is_not_admin_to_change_other_user_account(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_is_not_admin_to_change_other_user_account",
            user_id=user.id,
            other_user_id=other_user_id,
            other_user_account=(
                None if other_user is None else other_user.account.stars
            ),
            other_user_account_stars_vector=other_user_account_stars_vector,
        )

    async def user_set_other_user_account(
        self, user: User, other_user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_set_other_user_account",
            user_id=user.id,
            other_user_id=other_user.id,
            other_user_account_stars=other_user.account.stars,
        )

    async def user_changed_other_user_account(
        self,
        user: User,
        other_user: User,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_changed_other_user_account",
            user_id=user.id,
            other_user_id=other_user.id,
            other_user_account_stars=other_user.account.stars,
            other_user_account_stars_vector=other_user_account_stars_vector,
        )

    async def negative_account_on_change_other_user_account(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None:
        await self._logger.ainfo(
            "negative_account_on_change_other_user_account",
            user_id=user.id,
            other_user_id=other_user_id,
            other_user_account_stars_vector=other_user_account_stars_vector,
            other_user_account_stars=(
                None if other_user is None else other_user.account.stars
            ),
        )

    async def negative_account_on_set_other_user_account(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars: Stars,
        /,
    ) -> None:
        await self._logger.ainfo(
            "negative_account_on_change_other_user_account",
            user_id=user.id,
            other_user_id=other_user_id,
            other_user_account_stars=other_user_account_stars,
        )
