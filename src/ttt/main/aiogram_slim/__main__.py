import asyncio
import logging

from aiogram import Bot, Dispatcher
from dishka.integrations.aiogram import setup_dishka

from ttt.main.aiogram.di import container


async def amain() -> None:
    dp = await container.get(Dispatcher)
    setup_dishka(container, dp)

    logging.basicConfig(level=logging.INFO)

    bot = await container.get(Bot)
    await dp.start_polling(bot)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
