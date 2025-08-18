import logging

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

from ttt.presentation.unkillable_tasks import UnkillableTasks


async def start_aiogram(container: AsyncContainer) -> None:
    dp = await container.get(Dispatcher)
    setup_dishka(container, dp)

    async with container({TelegramObject: None}) as request:
        tasks = await request.get(UnkillableTasks)

    logging.basicConfig(level=logging.INFO)

    bot = await container.get(Bot)

    try:
        async with tasks:
            await dp.start_polling(bot)
    finally:
        await container.close()
