import asyncio

import sentry_sdk
from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider

from ttt import __version__
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.structlog.logger import LoggerFactory, ProdLoggerFactory
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
            LoggerFactory: ProdLoggerFactory(adds_request_id=True),
        },
    )

    secrets = await container.get(Secrets)
    sentry_sdk.init(dsn=secrets.sentry_dsn, release=__version__)

    await start_aiogram(container)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
