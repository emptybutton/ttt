from collections.abc import AsyncIterable
from dataclasses import dataclass, field

from aiogram import Bot

from ttt.application.player.ports.stars_purchase_payment_gateway import (
    PaidStarsPurchasePayment,
    StarsPurchasePaymentGateway,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.stars_purchase import StarsPurchase
from ttt.infrastructure.nats.paid_stars_purchase_payment_inbox import (
    InNatsPaidStarsPurchasePaymentInbox,
)
from ttt.presentation.aiogram.player.invoices import stars_invoce


@dataclass
class AiogramInAndNatsOutStarsPurchasePaymentGateway(
    StarsPurchasePaymentGateway,
):
    _paid_purchase_payment_inbox: InNatsPaidStarsPurchasePaymentInbox
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
        async for payment in self._paid_purchase_payment_inbox:
            yield payment
