import asyncio

import sentry_sdk
from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider

from ttt import __version__
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.main.common.di import InfrastructureProvider
from ttt.main.tg_bot.di import (
    ApplicationProvider,
    PresentationProvider,
)
from ttt.main.tg_bot.start_tg_bot import start_tg_bot
from ttt.main.tg_bot_prod.di import (
    ProdTgBotAppLoggerProvider,
    ProdTgBotRequestLoggerProvider,
)


async def amain() -> None:
    container = make_async_container(
        AiogramProvider(),
        ApplicationProvider(),
        PresentationProvider(),
        InfrastructureProvider(),
        ProdTgBotAppLoggerProvider(),
        ProdTgBotRequestLoggerProvider(),
    )

    secrets = await container.get(Secrets)
    sentry_sdk.init(dsn=secrets.sentry_dsn, release=__version__)

    await start_tg_bot(container)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
