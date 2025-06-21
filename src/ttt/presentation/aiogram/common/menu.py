from aiogram import Bot
from aiogram.types import BotCommand


async def set_menu(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="game", description="Начать поиск игры"),
        BotCommand(
            command="info", description="Показать информацию о пользователе"),
        BotCommand(command="help", description="Справка"),
    ])
