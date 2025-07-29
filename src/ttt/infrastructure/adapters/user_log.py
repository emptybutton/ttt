from dataclasses import dataclass
from uuid import UUID

from structlog.types import FilteringBoundLogger

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
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
            chat_id=user.id,
            user_id=user.id,
        )

    async def user_double_registration(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_double_registration",
            chat_id=user.id,
            user_id=user.id,
        )

    async def user_viewed(self, user_id: int, /) -> None:
        await self._logger.ainfo(
            "user_viewed",
            chat_id=user_id,
            user_id=user_id,
        )

    async def user_removed_emoji(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_removed_emoji",
            chat_id=user.id,
            user_id=user.id,
        )

    async def menu_viewed(self, user_id: int) -> None:
        await self._logger.ainfo(
            "menu_viewed",
            chat_id=user_id,
            user_id=user_id,
        )

    async def emoji_menu_viewed(self, user_id: int) -> None:
        await self._logger.ainfo(
            "emoji_menu_viewed",
            chat_id=user_id,
            user_id=user_id,
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
            chat_id=user.id,
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
            chat_id=user_id,
            user_id=user_id,
        )

    async def emoji_already_purchased_to_buy(
        self,
        user: User,
        emoji: Emoji,
    ) -> None:
        await self._logger.ainfo(
            "emoji_already_purchased_to_buy",
            chat_id=user.id,
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
            chat_id=user.id,
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
            chat_id=user_id,
            user_id=user_id,
        )

    async def emoji_not_purchased_to_select(
        self,
        user: User,
        emoji: Emoji,
    ) -> None:
        await self._logger.ainfo(
            "emoji_not_purchased_to_select",
            chat_id=user.id,
            user_id=user.id,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogStarsPurchaseUserLog(StarsPurchaseUserLog):
    _logger: FilteringBoundLogger

    async def user_intends_to_buy_stars(
        self,
        user_id: int,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_buy_stars",
            chat_id=user_id,
            user_id=user_id,
        )

    async def user_started_stars_puchase(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_started_stars_puchase",
            chat_id=user.id,
            user_id=user.id,
        )

    async def user_started_stars_puchase_payment(
        self,
        user: User,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_started_stars_puchase_payment",
            user_id=user.id,
        )

    async def stars_purchase_payment_completion_started(
        self,
        payment: PaidStarsPurchasePayment,
        /,
    ) -> None:
        await self._logger.ainfo(
            "stars_purchase_payment_completion_started",
            user_id=payment.user_id,
            chat_id=payment.user_id,
            purchase_id=payment.purchase_id.hex,
        )

    async def stars_purchase_payment_completed(
        self,
        user: User,
        payment: PaidStarsPurchasePayment,
        /,
    ) -> None:
        await self._logger.ainfo(
            "stars_purchase_payment_completed",
            user_id=payment.user_id,
            chat_id=payment.user_id,
            purchase_id=payment.purchase_id.hex,
        )

    async def double_stars_purchase_payment_completion(
        self,
        user: User,
        paid_payment: PaidStarsPurchasePayment,
    ) -> None:
        await self._logger.awarning(
            "double_stars_purchase_payment_completion",
            user_id=paid_payment.user_id,
            chat_id=paid_payment.user_id,
            purchase_id=paid_payment.purchase_id.hex,
        )

    async def invalid_stars_for_stars_purchase(
        self,
        user: User,
        stars: Stars,
    ) -> None:
        await self._logger.aerror(
            "invalid_stars_for_stars_purchase",
            user_id=user.id,
            chat_id=user.id,
            stars=stars,
        )

    async def double_stars_purchase_payment_start(
        self,
        user: User,
        purchase_id: UUID,
    ) -> None:
        await self._logger.ainfo(
            "double_stars_purchase_payment_start",
            user_id=user.id,
            purchase_id=purchase_id.hex,
        )

    async def no_purchase_to_start_stars_purchase_payment(
        self,
        user: User,
        purchase_id: UUID,
    ) -> None:
        await self._logger.aerror(
            "no_purchase_to_start_stars_purchase_payment",
            user_id=user.id,
            purchase_id=purchase_id.hex,
        )
