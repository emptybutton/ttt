from aiogram.methods import SendMessage
from aiogram.types.message import Message
from aiogram.utils.formatting import (
    Bold,
    Text,
    as_list,
    as_marked_section,
)


def need_to_start_message(message: Message) -> SendMessage:
    return message.answer("❌ Для начала необходимо начать: /start")


def help_message(message: Message) -> SendMessage:
    description = Text(
        Bold("ttt!"),
        " — многопользовательские онлайн-крестики-нолики в Telegram.",
    )

    content = as_list(
        description,
        as_marked_section(
            "Комманды:",
            Text(Bold("/game"), " — начать игру"),
            Text(Bold("/info"), " — посмотреть информацию о себе"),
            Text(Bold("/help"), " — вывести это сообщение"),
            marker="  ",
        ),
        sep="\n\n",
    )
    return message.answer(**content.as_kwargs())
