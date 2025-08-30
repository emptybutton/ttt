import logging

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import (
    AiogramMiddlewareData,
    ContainerMiddleware,
)

from ttt.presentation.unkillable_tasks import UnkillableTasks


async def start_aiogram(container: AsyncContainer) -> None:
    dp = await container.get(Dispatcher)

    middleware = ContainerMiddleware(container)

    for observer in dp.observers.values():
        observer.middleware(middleware)

    context = {TelegramObject: None, AiogramMiddlewareData: None}
    async with container(context) as request:
        tasks = await request.get(UnkillableTasks)

    logging.basicConfig(level=logging.INFO)

    bot = await container.get(Bot)

    try:
        async with tasks:
            await dp.start_polling(bot)
    finally:
        await container.close()
