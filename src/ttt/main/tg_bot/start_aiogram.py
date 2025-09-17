import logging
from functools import partial

from aiogram import Bot, Dispatcher
from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import (
    AiogramMiddlewareData,
    ContainerMiddleware,
)

from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.presentation.tasks.auto_cancel_invitation_to_game_task import (
    auto_cancel_invitation_to_game_task,
)
from ttt.presentation.tasks.matchmake_tasks import matchmake_tasks
from ttt.presentation.unkillable_tasks import UnkillableTasks


async def start_aiogram(container: AsyncContainer) -> None:
    dp = await container.get(Dispatcher)
    envs = await container.get(Envs)

    middleware = ContainerMiddleware(container)

    for observer in dp.observers.values():
        observer.middleware(middleware)

    context = {TelegramObject: None, AiogramMiddlewareData: None}
    async with container(context) as request:
        tasks = await request.get(UnkillableTasks)
        tasks.add(partial(auto_cancel_invitation_to_game_task, container))
        tasks.add(partial(
            matchmake_tasks,
            container,
            max_workers=envs.matchmaking_max_workers,
            worker_creation_interval_seconds=(
                envs.matchmaking_worker_creation_interval_seconds
            ),
        ))

    logging.basicConfig(level=logging.INFO)

    bot = await container.get(Bot)

    try:
        async with tasks:
            await dp.start_polling(bot)
    finally:
        await container.close()
