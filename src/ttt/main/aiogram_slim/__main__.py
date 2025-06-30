import asyncio

from ttt.main.aiogram.start_aiogram import start_aiogram


def main() -> None:
    asyncio.run(start_aiogram())


if __name__ == "__main__":
    main()
