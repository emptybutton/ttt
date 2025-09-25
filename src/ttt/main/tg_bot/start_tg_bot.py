import logging
from asyncio import CancelledError, TaskGroup
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import AiogramMiddlewareData
from taskiq import TaskiqMessage

from ttt.infrastructure.processors.processors import Processors
from ttt.infrastructure.taskiq.broker import NatsBroker
from ttt.infrastructure.taskiq.middlewares import TaskiqNextContainerMiddleware
from ttt.infrastructure.taskiq.worker import TaskiqBgWorker
from ttt.main.common.next_container import NextContainerWithFilledContext
from ttt.presentation.aiogram.common.middlewares import (
    AiogramNextContainerMiddleware,
)


async def start_tg_bot(container: AsyncContainer) -> None:
    next_container = NextContainerWithFilledContext(
        container,
        (TelegramObject, AiogramMiddlewareData, TaskiqMessage),
    )

    dp = await container.get(Dispatcher)
    middleware = AiogramNextContainerMiddleware(next_container)
    for observer in dp.observers.values():
        observer.middleware(middleware)

    nats_broker = await container.get(NatsBroker)
    nats_broker.add_middlewares(TaskiqNextContainerMiddleware(next_container))

    taskiq_bg_worker = await container.get(TaskiqBgWorker)
    processors = await container.get(Processors)
    bot = await container.get(Bot)

    logging.basicConfig(level=logging.INFO)

    try:
        with suppress(CancelledError):
            async with TaskGroup() as tasks:
                tasks.create_task(processors(next_container))
                await taskiq_bg_worker()
                await dp.start_polling(bot)
                raise CancelledError
    finally:
        await container.close()
