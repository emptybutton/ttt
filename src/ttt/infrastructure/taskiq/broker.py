from collections.abc import AsyncGenerator
from typing import NewType, Protocol

from nats.aio.msg import Msg as NatsMessage
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js import JetStreamContext
from taskiq import (
    AckableMessage,
    AsyncBroker,
    BrokerMessage,
)


class PullSubscribe(Protocol):
    async def __call__(
        self, js: JetStreamContext, subject: str, /,
    ) ->  JetStreamContext.PullSubscription: ...


class NatsBroker(AsyncBroker):
    _consumer: JetStreamContext.PullSubscription
    js: JetStreamContext

    def __init__(
        self,
        subject: str,
        pull_subscribe: PullSubscribe,
        pull_consume_batch: int = 1,
        pull_consume_timeout: float | None = 5,
    ) -> None:
        super().__init__()
        self._subject = subject
        self._pull_subscribe = pull_subscribe
        self._pull_consume_batch = pull_consume_batch
        self._pull_consume_timeout = pull_consume_timeout

    async def startup(self) -> None:
        await super().startup()
        self._consumer = await self._pull_subscribe(self.js, self._subject)

    async def kick(self, message: BrokerMessage) -> None:
        await self.js.publish(
            self._subject,
            payload=message.message,
            headers=message.labels,
        )

    async def listen(self) -> AsyncGenerator[AckableMessage]:
        while True:
            try:
                nats_messages: list[NatsMessage] = await self._consumer.fetch(
                    batch=self._pull_consume_batch,
                    timeout=self._pull_consume_timeout,
                )
                for nats_message in nats_messages:
                    yield AckableMessage(
                        data=nats_message.data,
                        ack=nats_message.ack,
                    )
            except NatsTimeoutError:
                continue


NatsBrokers = NewType("NatsBrokers", tuple[NatsBroker, ...])
