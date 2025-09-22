import logging
from asyncio import gather
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import (
    AiogramMiddlewareData,
    ContainerMiddleware,
)
from dishka.integrations.taskiq import setup_dishka
from taskiq.api.receiver import run_receiver_task

from ttt.infrastructure.taskiq.broker import NatsBrokers
from ttt.presentation.tasks.unkillable_tasks import UnkillableTasks


async def start_tg_bot(container: AsyncContainer) -> None:
    dp = await container.get(Dispatcher)
    middleware = ContainerMiddleware(container)

    for observer in dp.observers.values():
        observer.middleware(middleware)

    logging.basicConfig(level=logging.INFO)

    tasks = await container.get(UnkillableTasks)
    next_container = partial(
        container, {TelegramObject: None, AiogramMiddlewareData: None},
    )
    await tasks(next_container)

    nats_brokers = await container.get(NatsBrokers)

    for broker in nats_brokers:
        setup_dishka(container, broker)

    await gather(*(
        broker.startup()
        for broker in nats_brokers
    ))

    bot = await container.get(Bot)

    try:
        await gather(
            dp.start_polling(bot),
            gather(*(run_receiver_task(broker) for broker in nats_brokers)),
        )
    finally:
        await container.close()
