import json
from asyncio import (
    AbstractEventLoop,
    Semaphore,
    Task,
    gather,
    get_event_loop,
)
from collections.abc import (
    AsyncIterator,
    Callable,
)
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol, Self

from dishka import AsyncContainer
from nats.aio.msg import Msg as NatsMessage
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js import JetStreamContext
from structlog.types import FilteringBoundLogger

from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.dishka.next_container import NextContainer
from ttt.infrastructure.structlog.logger import (
    unexpected_error_log,
)


class PullSubscribe(Protocol):
    async def __call__(
        self, js: JetStreamContext, subject: str,
    ) -> JetStreamContext.PullSubscription: ...


class NatsRemoteFuncBody[**PmT](Protocol):
    async def __call__(
        self,
        container: AsyncContainer,
        *args: PmT.args,
        **kwargs: PmT.kwargs,
    ) -> Any: ...  # noqa: ANN401


@dataclass
class NatsRemoteFunc[**PmT = ...]:
    body: NatsRemoteFuncBody[PmT]
    _pull_subscribe: PullSubscribe
    _subject: str

    _max_workers: int | None = None
    _pull_consume_batch: int | None = None
    _pull_consume_timeout: float | None = None

    _js: JetStreamContext = field(init=False)
    _pull_subscription: JetStreamContext.PullSubscription = field(init=False)
    _workers: set[Task[None]] = field(init=False, default_factory=set)
    _semaphore: Semaphore = field(init=False, default_factory=Semaphore)
    _container: AsyncContainer = field(init=False)
    _loop: AbstractEventLoop = field(init=False)

    @asynccontextmanager
    async def startup(
        self,
        js: JetStreamContext,
        max_workers: int | None = None,
        pull_consume_batch: int | None = None,
        pull_consume_timeout: float | None = None,
    ) -> AsyncIterator[Self]:
        self._loop = get_event_loop()
        self._max_workers = max_workers or self._max_workers or 1000
        self._pull_consume_batch = (
            pull_consume_batch or self._pull_consume_batch or 1
        )
        self._pull_consume_timeout = (
            pull_consume_timeout or self._pull_consume_timeout or 5
        )

        self._js = js
        self._pull_subscription = await self._pull_subscribe(
            self._js,
            self._subject,
        )
        self._semaphore = Semaphore(self._max_workers)

        try:
            yield self
        finally:
            await gather(*self._workers)

    async def __call__(self, *args: PmT.args, **kwargs: PmT.kwargs) -> None:
        payload = {"args": args, "kwargs": kwargs}

        await not_none(self._js).publish(
            self._subject,
            payload=json.dumps(payload).encode(),
        )

    async def processor(self, next_container: NextContainer) -> None:
        while True:
            try:
                messages = await self._pull_subscription.fetch(
                    batch=not_none(self._pull_consume_batch),
                    timeout=self._pull_consume_timeout,
                )
            except NatsTimeoutError:
                continue

            for message in messages:
                await self._create_worker(message, next_container)

    async def _create_worker(
        self, message: NatsMessage, next_container: NextContainer,
    ) -> None:
        await self._semaphore.acquire()
        task = self._loop.create_task(self._worker(message, next_container))
        self._workers.add(task)
        task.add_done_callback(self._workers.discard)

    async def _worker(
        self, message: NatsMessage, next_container: NextContainer,
    ) -> None:
        async with next_container() as container:
            try:
                json_str = message.data.decode()
                json_ = json.loads(json_str)
                await self.body(container, *json_["args"], **json_["kwargs"])
            except Exception as error:  # noqa: BLE001
                await message.nak()

                logger = await container.get(FilteringBoundLogger)
                await unexpected_error_log(logger, error)

                self._semaphore.release()
            except BaseException as error:
                await message.nak()
                self._semaphore.release()
                raise error from error
            else:
                await message.ack()
                self._semaphore.release()


def nats_remote[**PmT](
    subject: str,
    pull_subscribe: PullSubscribe,
    max_workers: int | None = None,
    pull_consume_batch: int | None = None,
    pull_consume_timeout: float | None = None,
) -> Callable[[NatsRemoteFuncBody[PmT]], NatsRemoteFunc[PmT]]:
    def decorator(body: NatsRemoteFuncBody[PmT]) -> NatsRemoteFunc[PmT]:
        return NatsRemoteFunc(
            body,
            pull_subscribe,
            subject,
            max_workers,
            pull_consume_batch,
            pull_consume_timeout,
        )

    return decorator
