from aiogram import Bot


async def need_to_start_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Для начала необходимо начать: /start")
