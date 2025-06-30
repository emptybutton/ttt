from aiogram import Bot
from aiogram.utils.formatting import (
    Bold,
    Italic,
    Text,
    Underline,
    as_list,
    as_marked_section,
)


async def anons_are_rohibited_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Анонимам вход запрещён.")


async def need_to_start_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Для начала необходимо начать: /start")


async def help_message(bot: Bot, chat_id: int) -> None:
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
            Text(Bold("/select_emoji"), " — выбрать эмоджи"),
            Text(Bold("/remove_emoji"), " — убрать выбранный эмоджи"),
            Text(Bold("/buy_emoji"), " — купить эмоджи"),
            Text(Bold("/buy_stars"), " — купить звёзды"),
            Text(Bold("/help"), " — вывести это сообщение"),
            marker="  ",
        ),
        sep="\n\n",
    )
    await bot.send_message(chat_id, **content.as_kwargs())
