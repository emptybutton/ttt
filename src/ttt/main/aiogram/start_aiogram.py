import logging
from asyncio import gather
from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider as DishkaAiogramProvider
from dishka.integrations.aiogram import setup_dishka

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.infrastructure.buffer import Buffer
from ttt.infrastructure.structlog.logger import LoggerFactory
from ttt.main.aiogram.di import (
    AiogramProvider,
    AiogramRequestDataProvider,
    ApplicationWithAiogramRequestDataProvider,
    ApplicationWithoutAiogramRequestDataProvider,
)
from ttt.main.common.di import InfrastructureProvider
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
