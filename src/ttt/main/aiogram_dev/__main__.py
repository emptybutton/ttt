import asyncio

from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.structlog.logger import DevLoggerFactory
from ttt.main.aiogram.di import aiogram_containers
from ttt.main.aiogram.start_aiogram import start_aiogram


async def amain() -> None:
    containers = aiogram_containers(DevLoggerFactory())
    await start_aiogram(containers)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
