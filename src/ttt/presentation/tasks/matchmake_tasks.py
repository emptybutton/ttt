from asyncio import Semaphore, TaskGroup, sleep

from aiogram.types import TelegramObject
from dishka import AsyncContainer
from dishka.integrations.aiogram import AiogramMiddlewareData

from ttt.application.user.game.matchmake import Matchmake


async def matchmake_tasks(
    diska_container: AsyncContainer,
    max_workers: int,
    worker_creation_interval_seconds: float,
) -> None:
    semaphore = Semaphore(max_workers)

    async with TaskGroup() as tasks:
        while True:
            await sleep(worker_creation_interval_seconds)
            if not semaphore.locked():
                tasks.create_task(_matchmake_task(diska_container, semaphore))


async def _matchmake_task(
    diska_container: AsyncContainer, semaphore: Semaphore,
) -> None:
    context = {TelegramObject: None, AiogramMiddlewareData: None}
    async with semaphore, diska_container(context) as request:
        matchmake = await request.get(Matchmake)
        await matchmake()
