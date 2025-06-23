from aiogram import Bot
from aiogram.types import BotCommand


async def ttt_bot(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="game", description="Начать поиск игры"),
        BotCommand(command="profile", description="Показать профиль"),
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Справка"),
    ])
