from collections.abc import AsyncIterable
from dataclasses import dataclass, field

from aiogram import Bot

from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.infrastructure.buffer import Buffer
from ttt.presentation.aiogram.player.invoices import stars_invoce


@dataclass
class AiogramInAndBufferOutStarsPurchasePaymentGateway(
    StarsPurchasePaymentGateway,
):
    _buffer: Buffer[PaidStarsPurchasePayment]
    _bot: Bot
    _payments_token: str = field(repr=False)

    async def process_payment(
        self,
        purshase: StarsPurchase,
        location: PlayerLocation,
    ) -> None:
        await stars_invoce(self._bot, location, purshase, self._payments_token)

    async def paid_payment_stream(
        self,
    ) -> AsyncIterable[PaidStarsPurchasePayment]:
        async for payment in self._buffer.stream():
            yield payment
