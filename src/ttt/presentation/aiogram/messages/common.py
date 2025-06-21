from aiogram.types.message import Message


async def anons_are_rohibited_message(message: Message) -> None:
    await message.answer("❌ Анонимам вход запрещён.")
