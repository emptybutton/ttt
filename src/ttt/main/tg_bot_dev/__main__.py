import asyncio

from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider

from ttt.main.common.di import InfrastructureProvider
from ttt.main.tg_bot.di import (
    ApplicationProvider,
    PresentationProvider,
)
from ttt.main.tg_bot.start_tg_bot import start_tg_bot
from ttt.main.tg_bot_dev.di import (
    DevTgBotAppLoggerProvider,
    DevTgBotRequestLoggerProvider,
)


async def amain() -> None:
    container = make_async_container(
        AiogramProvider(),
        ApplicationProvider(),
        PresentationProvider(),
        InfrastructureProvider(),
        DevTgBotRequestLoggerProvider(),
        DevTgBotAppLoggerProvider(),
    )

    await start_tg_bot(container)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
