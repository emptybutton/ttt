import asyncio

import sentry_sdk

from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.structlog.logger import ProdLoggerFactory
from ttt.main.aiogram.di import aiogram_containers
from ttt.main.aiogram.start_aiogram import start_aiogram


async def amain() -> None:
    containers = aiogram_containers(ProdLoggerFactory())

    secrets = await containers.container_without_request_data.get(Secrets)
    sentry_sdk.init(secrets.sentry_dsn)

    await start_aiogram(containers)


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
