import logging
from asyncio import CancelledError, TaskGroup
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import AiogramMiddlewareData

from ttt.infrastructure.processors.processor import Processor
from ttt.main.common.next_container import NextContainerWithFilledContext
from ttt.presentation.aiogram.common.middlewares import (
    AiogramNextContainerMiddleware,
)


async def start_tg_bot(container: AsyncContainer) -> None:
    next_container = NextContainerWithFilledContext(
        container,
        (TelegramObject, AiogramMiddlewareData),
    )

    dp = await container.get(Dispatcher)
    middleware = AiogramNextContainerMiddleware(next_container)
    for observer in dp.observers.values():
        observer.middleware(middleware)

    processors = await container.get(tuple[Processor, ...])
    bot = await container.get(Bot)

    logging.basicConfig(level=logging.INFO)

    try:
        with suppress(CancelledError):
            async with TaskGroup() as tasks:
                for processor in processors:
                    tasks.create_task(processor(next_container))
                await dp.start_polling(bot)
                raise CancelledError
    finally:
        await container.close()
