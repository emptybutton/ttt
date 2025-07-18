from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from types import TracebackType
from typing import ClassVar, Self, cast

from nats.js import JetStreamContext
from pydantic import TypeAdapter

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.infrastructure.nats.messages import at_least_once_messages


@dataclass
class InNatsPaidStarsPurchasePaymentInbox:
    _js: JetStreamContext

    _subscription: JetStreamContext.PullSubscription = field(init=False)
    _adapter: ClassVar = TypeAdapter(PaidStarsPurchasePayment)
    _subject: ClassVar = "user.stars_purchase.paid_payment_inbox"

    async def __aenter__(self) -> Self:
        self._subscription = await self._js.pull_subscribe(
            self._subject,
            "ttt-user-stars_purchase-paid_payment_inbox",
            "USER",
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
        async for message in at_least_once_messages(self._subscription):
            yield cast(
                PaidStarsPurchasePayment,
                self._adapter.validate_json(message.data),
            )
