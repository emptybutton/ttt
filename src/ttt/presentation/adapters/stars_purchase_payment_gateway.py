from collections.abc import AsyncIterable
from dataclasses import dataclass, field
from uuid import UUID

from aiogram import Bot
from aiogram.types import PreCheckoutQuery

from ttt.application.player.common.dto.common import PaidStarsPurchasePayment
from ttt.application.player.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.buffer import Buffer
from ttt.presentation.aiogram.player.invoices import stars_invoce


@dataclass
class AiogramInAndBufferOutStarsPurchasePaymentGateway(
    StarsPurchasePaymentGateway,
):
    _pre_checkout_query: PreCheckoutQuery | None
    _buffer: Buffer[PaidStarsPurchasePayment]
    _bot: Bot
    _payments_token: str = field(repr=False)

    async def send_invoice(
        self,
        purshase: StarsPurchase,
        location: PlayerLocation,
    ) -> None:
        await stars_invoce(self._bot, location, purshase, self._payments_token)

    async def start_payment(self, payment_id: UUID) -> None:
        await not_none(self._pre_checkout_query).answer(ok=True)

    async def stop_payment_due_to_dublicate(self, payment_id: UUID) -> None:
        message = "С одного инвойса можно покупать только один раз"

        await not_none(self._pre_checkout_query).answer(
            ok=False, error_message=message,
        )

    async def stop_payment_due_to_error(self, payment_id: UUID) -> None:
        message = "Неожиданная ошибка. Попробуйте позже!"

        await not_none(self._pre_checkout_query).answer(
            ok=False, error_message=message,
        )

    async def paid_payment_stream(
        self,
    ) -> AsyncIterable[PaidStarsPurchasePayment]:
        async for payment in self._buffer.stream():
            yield payment
