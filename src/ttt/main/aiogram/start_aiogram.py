import logging
from asyncio import gather

from aiogram import Bot, Dispatcher
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

from ttt.presentation.unkillable_tasks import UnkillableTasks


async def start_aiogram(
    container_with_request_data: AsyncContainer,
    container_without_request_data: AsyncContainer,
) -> None:
    dp = await container_with_request_data.get(Dispatcher)
    setup_dishka(container_with_request_data, dp)

    async with container_without_request_data() as request:
        tasks = await request.get(UnkillableTasks)

    logging.basicConfig(level=logging.INFO)

    bot = await container_with_request_data.get(Bot)

    try:
        async with tasks:
            await dp.start_polling(bot)
    finally:
        await gather(
            container_with_request_data.close(),
            container_without_request_data.close(),
            return_exceptions=True,
        )
