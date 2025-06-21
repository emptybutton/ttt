import asyncio

from ttt.main.aiogram.di import container
from ttt.main.aiogram.start_aiogram import start_aiogram


def main() -> None:
    asyncio.run(start_aiogram(container))


if __name__ == "__main__":
    main()
