import asyncio

from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider

from ttt.infrastructure.structlog.logger import (
    DevLoggerFactory,
    LoggerFactory,
)
from ttt.main.common.di import InfrastructureProvider
from ttt.main.tg_bot.di import (
    ApplicationProvider,
    PresentationProvider,
)
from ttt.main.tg_bot.start_aiogram import start_aiogram


async def amain() -> None:
    container = make_async_container(
        AiogramProvider(),
        ApplicationProvider(),
        PresentationProvider(),
        InfrastructureProvider(),
        context={
            LoggerFactory: DevLoggerFactory(adds_request_id=True),
        },
    )

    await start_aiogram(container)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
