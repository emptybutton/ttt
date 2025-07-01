from collections.abc import AsyncIterable
from dataclasses import dataclass

from aiogram import Bot
from aiogram.types import PreCheckoutQuery

from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.infrastructure.buffer import Buffer


@dataclass
class AiogramStarsPurchasePaymentGateway(
    StarsPurchasePaymentGateway,
):
    _buffer: Buffer[PaidStarsPurchasePayment]
    _bot: Bot
    _pre_checkout_query: PreCheckoutQuery

    async def start_payment(self, location: PlayerLocation) -> None:
        await self._pre_checkout_query.answer(ok=True)

    async def paid_payment_stream(
        self,
    ) -> AsyncIterable[PaidStarsPurchasePayment]:
        async for payment in self._buffer.stream():
            yield payment
