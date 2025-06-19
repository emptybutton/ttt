from aiogram.methods import SendMessage
from aiogram.types.message import Message
from aiogram.utils.formatting import (
    Bold,
    as_list,
    as_marked_section,
)


def need_to_start_message(message: Message) -> SendMessage:
    return message.answer("❌ Для начала необходимо начать: /start")


def help_message(message: Message) -> SendMessage:
    content = as_list(
         as_marked_section(
            f"{Bold("ttt!"):}",
            "Многопользовательские онлайн-крестики-нолики в Telegram.",
            marker="  ",
        ),
        as_marked_section(
            "Комманды:",
            "/game - чтобы начать игру",
            "/info - чтобы посмотреть информацию о себе",
            "/help - чтобы вывести это сообщение",
            marker="  ",
        ),
        sep="\n\n",
    )
    return message.answer(**content.as_kwargs())
