import asyncio

from watchfiles import run_process

from ttt.main.aiogram.di import container
from ttt.main.aiogram.start_aiogram import start_aiogram


def run_aiogram() -> None:
    asyncio.run(start_aiogram(container))


def main() -> None:
    run_process("./src", target=run_aiogram)


if __name__ == "__main__":
    main()
