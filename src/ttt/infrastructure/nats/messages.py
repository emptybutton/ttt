from collections.abc import AsyncIterator

from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js import JetStreamContext


async def at_least_once_messages(
    subscription: JetStreamContext.PullSubscription,
    batch: int = 1,
    timeout: float | None = 5,  # noqa: ASYNC109
    heartbeat: float | None = None,
) -> AsyncIterator[Msg]:
    while True:
        try:
            messages = await subscription.fetch(batch, timeout, heartbeat)
        except NatsTimeoutError:
            continue

        for message in messages:
            try:
                yield message
            except BaseException as error:
                await message.nak()
                raise error from error
            else:
                await message.ack()
