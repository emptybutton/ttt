from asyncio import Queue, TaskGroup, gather
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, overload

from nats.aio.msg import Msg as NatsMessage
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js import JetStreamContext
from taskiq import (
    AckableMessage,
    AsyncBroker,
    AsyncTaskiqDecoratedTask,
    BrokerMessage,
)


@dataclass(frozen=True)
class PullSubscribe:
    _func: Callable[
        [JetStreamContext, str], Awaitable[JetStreamContext.PullSubscription],
    ]

    async def __call__(
        self, js: JetStreamContext, subject: str,
    ) -> JetStreamContext.PullSubscription:
        return await self._func(js, subject)


@dataclass
class NatsQueue:
    _subject: str
    _pull_subscribe: PullSubscribe
    _pull_consume_batch: int
    _pull_consume_timeout: float | None

    _js: JetStreamContext = field(init=False)
    _pull_subscription: JetStreamContext.PullSubscription = field(init=False)

    async def startup(self, js: JetStreamContext) -> None:
        self._js = js
        self._pull_subscription = await self._pull_subscribe(js, self._subject)

    async def push(self, message: BrokerMessage) -> None:
        await self._js.publish(
            self._subject,
            payload=message.message,
            headers=message.labels,
        )

    async def pull_to(self, output: Queue[AckableMessage]) -> None:
        nats_messages: list[NatsMessage]

        while True:
            try:
                nats_messages = await self._pull_subscription.fetch(
                    batch=self._pull_consume_batch,
                    timeout=self._pull_consume_timeout,
                )
            except NatsTimeoutError:
                continue

            ackable_messages = (
                AckableMessage(
                    data=nats_message.data,
                    ack=nats_message.ack,
                )
                for nats_message in nats_messages
            )
            await gather(*(
                output.put(ackable_message)
                for ackable_message in ackable_messages
            ))


class NatsBroker(AsyncBroker):
    js: JetStreamContext
    pulling_queue: Queue[AckableMessage]

    def __init__(
        self,
        default_subject: str = "taskiq.>",
        default_pull_subscribe: PullSubscribe | None = None,
        default_pull_consume_batch: int = 1,
        default_pull_consume_timeout: float | None = 5,
    ) -> None:
        super().__init__()
        self._default_subject = default_subject
        self._default_pull_subscribe = (
            default_pull_subscribe
            or (lambda js, sub: js.pull_subscribe(
                sub,
                "taskiq",
                "TASKIQ",
            ))
        )
        self._default_pull_consume_batch = default_pull_consume_batch
        self._default_pull_consume_timeout = default_pull_consume_timeout
        self._queue_by_task_name = dict[str, NatsQueue]()

    @overload
    def task[**PmT, RT](
        self,
        task_name: Callable[PmT, RT],
        **labels: Any,  # noqa: ANN401
    ) -> AsyncTaskiqDecoratedTask[PmT, RT]:
        ...

    @overload
    def task[**PmT, RT](
        self,
        task_name: str | None = None,
        **labels: Any,  # noqa: ANN401
    ) -> Callable[
        [Callable[PmT, RT]],
        AsyncTaskiqDecoratedTask[PmT, RT],
    ]:
        ...

    def task[**PmT, RT](
        self,
        task_name: str | Callable[PmT, RT] | None = None,
        **labels: Any,
    ) -> Any:
        subject = labels.pop("subject", self._default_subject)
        pull_subscribe = labels.pop(
            "pull_subscribe", self._default_pull_subscribe,
        )
        pull_consume_batch = labels.pop(
            "pull_consume_batch", self._default_pull_consume_batch,
        )
        pull_consume_timeout = labels.pop(
            "pull_consume_timeout", self._default_pull_consume_timeout,
        )
        queue = NatsQueue(
            subject,
            pull_subscribe,
            pull_consume_batch,
            pull_consume_timeout,
        )

        result = super().task(task_name, **labels)

        if isinstance(result, AsyncTaskiqDecoratedTask):
            self._queue_by_task_name[result.task_name] = queue
            return result

        def decorator(
            func: Callable[PmT, RT],
        ) -> AsyncTaskiqDecoratedTask[PmT, RT]:
            task = result(func)
            self._queue_by_task_name[task.task_name] = queue
            return task

        return decorator

    async def startup(self) -> None:
        await super().startup()
        await gather(*(
            queue.startup(self.js)
            for queue in self._queue_by_task_name.values()
        ))

    async def kick(self, message: BrokerMessage) -> None:
        await self._queue_by_task_name[message.task_name].push(message)

    async def listen(self) -> AsyncGenerator[AckableMessage]:
        async with TaskGroup() as pulling_tasks:
            for nats_queue in self._queue_by_task_name.values():
                pulling_tasks.create_task(
                    nats_queue.pull_to(self.pulling_queue),
                )

            while True:
                yield await self.pulling_queue.get()
