from dataclasses import dataclass
from uuid import UUID

from structlog.types import FilteringBoundLogger

from ttt.application.stars_purchase.ports.stars_purchase_log import (
    StarsPurchaseLog,
)
from ttt.entities.core.stars import Stars
from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase
from ttt.entities.core.user.user import User
from ttt.entities.finance.payment.success import PaymentSuccess


@dataclass(frozen=True, unsafe_hash=False)
class StructlogStarsPurchaseLog(StarsPurchaseLog):
    _logger: FilteringBoundLogger

    async def stars_puchase_started(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None:
        await self._logger.ainfo(
            "stars_puchase_started",
            user_id=stars_purchase.user.id,
            stars_purchase_id=stars_purchase.id_.hex,
        )

    async def stars_puchase_payment_started(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None:
        await self._logger.ainfo(
            "stars_puchase_payment_started",
            user_id=stars_purchase.user.id,
            purchase_id=stars_purchase.id_.hex,
        )

    async def stars_purchase_payment_completion_started(
        self,
        purchase_id: UUID,
        success: PaymentSuccess,
        /,
    ) -> None:
        await self._logger.ainfo(
            "stars_purchase_payment_completion_started",
            purchase_id=purchase_id.hex,
        )

    async def stars_purchase_payment_completed(
        self,
        stars_purchase: StarsPurchase,
        success: PaymentSuccess,
        /,
    ) -> None:
        await self._logger.ainfo(
            "stars_purchase_payment_completed",
            purchase_id=stars_purchase.id_.hex,
        )

    async def double_stars_purchase_payment_completion(
        self,
        stars_purchase: StarsPurchase,
        success: PaymentSuccess,
    ) -> None:
        await self._logger.ainfo(
            "double_stars_purchase_payment_completion",
            purchase_id=stars_purchase.id_.hex,
        )

    async def invalid_stars_for_stars_purchase(
        self,
        user: User,
        stars: Stars,
    ) -> None:
        await self._logger.aerror(
            "invalid_stars_for_stars_purchase",
            stars=stars,
        )

    async def double_stars_purchase_payment_start(
        self,
        stars_purchase: StarsPurchase,
    ) -> None:
        await self._logger.ainfo(
            "double_stars_purchase_payment_start",
            purchase_id=stars_purchase.id_.hex,
        )

    async def no_stars_purchase_to_start_payment(
        self,
        purchase_id: UUID,
        /,
    ) -> None:
        await self._logger.aerror(
            "no_stars_purchase_to_start_payment",
            purchase_id=purchase_id.hex,
        )

    async def no_stars_purchase_to_complete_payment(
        self,
        purchase_id: UUID,
        /,
    ) -> None:
        await self._logger.aerror(
            "no_stars_purchase_to_complete_payment",
            purchase_id=purchase_id.hex,
        )
