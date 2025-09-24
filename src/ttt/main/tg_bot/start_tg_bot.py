import logging
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import (
    AiogramMiddlewareData,
    ContainerMiddleware,
)

from ttt.infrastructure.taskiq.worker import TaskiqBgWorker
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

    taskiq_bg_worker = await container.get(TaskiqBgWorker)
    bot = await container.get(Bot)

    try:
        await taskiq_bg_worker(container)
        await dp.start_polling(bot)
    finally:
        await container.close()
