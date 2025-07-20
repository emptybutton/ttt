from dataclasses import dataclass

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
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


@dataclass(frozen=True, unsafe_hash=False)
class StructlogCommonUserLog(CommonUserLog):
    _logger: FilteringBoundLogger

    async def user_registered(
        self, location: UserLocation, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_registered",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_double_registration(
        self, location: UserLocation, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_double_registration",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_viewed(self, location: UserLocation, /) -> None:
        await self._logger.ainfo(
            "user_viewed",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_removed_emoji(
        self, location: UserLocation, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_removed_emoji",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogEmojiPurchaseUserLog(EmojiPurchaseUserLog):
    _logger: FilteringBoundLogger

    async def user_bought_emoji(
        self, location: UserLocation, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_bought_emoji",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_intends_to_buy_emoji(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_buy_emoji",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogEmojiSelectionUserLog(EmojiSelectionUserLog):
    _logger: FilteringBoundLogger

    async def user_selected_emoji(
        self, location: UserLocation, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_selected_emoji",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_intends_to_select_emoji(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_select_emoji",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )


@dataclass(frozen=True, unsafe_hash=False)
class StructlogStarsPurchaseUserLog(StarsPurchaseUserLog):
    _logger: FilteringBoundLogger

    async def user_intends_to_buy_stars(
        self,
        location: UserLocation,
        /,
    ) -> None:
        await self._logger.ainfo(
            "user_intends_to_buy_stars",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_started_stars_puchase(
        self, location: UserLocation, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_started_stars_puchase",
            chat_id=location.chat_id,
            user_id=location.user_id,
        )

    async def user_started_stars_puchase_payment(
        self, user: User, /,
    ) -> None:
        await self._logger.ainfo(
            "user_started_stars_puchase_payment",
            user_id=user.id,
        )

    async def stars_purshase_payment_completion_started(
        self, payment: PaidStarsPurchasePayment, /,
    ) -> None:
        await self._logger.ainfo(
            "stars_purshase_payment_completion_started",
            user_id=payment.location.user_id,
            chat_id=payment.location.chat_id,
            purshase_id=payment.purshase_id,
        )

    async def stars_purshase_payment_completed(
        self, user: User, payment: PaidStarsPurchasePayment, /,
    ) -> None:
        await self._logger.ainfo(
            "stars_purshase_payment_completed",
            user_id=payment.location.user_id,
            chat_id=payment.location.chat_id,
            purshase_id=payment.purshase_id,
        )
