from aiogram import Bot


async def anons_are_rohibited_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Анонимам вход запрещён.")


async def need_to_start_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Для начала необходимо начать: /start")
