from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from types import TracebackType
from typing import ClassVar, Self, cast

from nats.js import JetStreamContext
from pydantic import TypeAdapter

from ttt.application.player.ports.stars_purchase_payment_gateway import (
    PaidStarsPurchasePayment,
)
from ttt.infrastructure.nats.subscription import pull_subscription


@dataclass
class InNatsPaidStarsPurchasePaymentInbox:
    _js: JetStreamContext

    _subscription: JetStreamContext.PullSubscription = field(init=False)
    _adapter: ClassVar = TypeAdapter(PaidStarsPurchasePayment)
    _subject: ClassVar = "player.stars_purchase.payment_paid"

    async def __aenter__(self) -> Self:
        self._subscription = await pull_subscription(
            self._js,
            self._subject,
            "PLAYER",
        )
        return self

    async def __aexit__(
        self,
        _: type[BaseException] | None,
        __: BaseException | None,
        ___: TracebackType | None,
    ) -> None: ...

    async def push(self, payment: PaidStarsPurchasePayment) -> None:
        json = self._adapter.dump_json(payment)
        await self._js.publish(self._subject, json)

    async def __aiter__(self) -> AsyncIterator[PaidStarsPurchasePayment]:
        messages = await self._subscription.fetch()

        for message in messages:
            paid_payment = cast(
                PaidStarsPurchasePayment,
                self._adapter.validate_json(message.data),
            )
            yield paid_payment
            await message.ack()
