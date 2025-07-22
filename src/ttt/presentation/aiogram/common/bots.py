from aiogram import Bot
from aiogram.types import BotCommand


async def ttt_bot(bot: Bot) -> None:
    await bot.set_my_commands([
        BotCommand(command="game", description="Начать игру"),
        BotCommand(command="game_with_ai", description="Начать игру c ИИ"),
        BotCommand(command="cancel_game", description="Отменить игру"),
        BotCommand(command="profile", description="Показать профиль"),
        BotCommand(command="select_emoji", description="Выбрать эмоджи"),
        BotCommand(
            command="remove_emoji",
            description="Убрать выбранный эмоджи",
        ),
        BotCommand(command="buy_emoji", description="Купить эмоджи"),
        BotCommand(command="buy_stars", description="Купить звёзды"),
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Справка"),
    ])
