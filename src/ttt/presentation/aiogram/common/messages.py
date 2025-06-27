from aiogram.types.message import Message
from aiogram.utils.formatting import (
    Bold,
    Italic,
    Text,
    Underline,
    as_list,
    as_marked_section,
)


async def anons_are_rohibited_message(message: Message) -> None:
    await message.answer("❌ Анонимам вход запрещён.")


async def need_to_start_message(message: Message) -> None:
    await message.answer("❌ Для начала необходимо начать: /start")


async def help_message(message: Message) -> None:
    description = Text(
        Underline(Italic(Bold("ttt!"))),
        " — многопользовательские онлайн-крестики-нолики в Telegram.",
    )

    description.as_kwargs()

    content = as_list(
        description,
        as_marked_section(
            "Комманды:",
            Text(Bold("/game"), " — начать игру"),
            Text(Bold("/cancel_game"), " — отменить игру"),
            Text(Bold("/profile"), " — показать профиль"),
            Text(Bold("/buy_emoji"), " — купить эмоджи"),
            Text(Bold("/help"), " — вывести это сообщение"),
            marker="  ",
        ),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())
