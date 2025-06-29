from nats.js import JetStreamContext
from nats.js.api import ConsumerConfig


async def pull_subscription(
    js: JetStreamContext,
    subject: str,
    stream: str,
) -> JetStreamContext.PullSubscription:
    return await js.pull_subscribe(
        subject,
        subject,
        stream,
        config=ConsumerConfig(deliver_group=subject),
    )
