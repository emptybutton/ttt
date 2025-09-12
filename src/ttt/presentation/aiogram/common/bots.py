from aiogram import Bot
from aiogram.types import BotCommand


async def ttt_bot(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="admin", description="Админ-панель"),
        BotCommand(command="start", description="Запустить бота"),
    ])
