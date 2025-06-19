from aiogram.methods import SendMessage
from aiogram.types.message import Message


def anons_are_rohibited_message(message: Message) -> SendMessage:
    return message.answer("❌ Анонимам вход запрещён.")
