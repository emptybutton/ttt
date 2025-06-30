from collections.abc import Sequence

from aiogram import Bot
from aiogram.utils.formatting import Bold, Text, as_list

from ttt.entities.core.stars import Stars
from ttt.presentation.aiogram.player.keyboards import stars_prices_keyboard


async def profile_message(  # noqa: PLR0913, PLR0917
    bot: Bot,
    chat_id: int,
    stars: int,
    emojis: Sequence[str],
    selected_emoji: str | None,
    number_of_wins: int,
    number_of_draws: int,
    number_of_defeats: int,
    is_in_game: bool,  # noqa: FBT001
) -> None:
    total = number_of_wins + number_of_defeats + number_of_draws

    if total > 0:
        winning_percentage = number_of_wins / total * 100
        winning_percentage_text = (
            f"{int(winning_percentage)}"
            if int(winning_percentage) == winning_percentage
            else f"{winning_percentage:.2f}"
        )
    else:
        winning_percentage_text = None

    if emojis:
        emoji_value_texts = (
            Text(Bold("<", selected_emoji, ">"))
            if emoji == selected_emoji
            else Text(emoji)
            for emoji in emojis
        )
        emoji_text_values = as_list(*emoji_value_texts, sep="")
        emoji_texts = [Text("🎭 Эмоджи: ", emoji_text_values)]
    else:
        emoji_texts = []

    content = as_list(
        f"🌟 Звёзд: {stars}",
        *emoji_texts,
        f"🏆 Побед: {number_of_wins}",
        f"💀 Поражений: {number_of_defeats}",
        f"🕊️ Ничьих: {number_of_draws}",
        *(
            []
            if winning_percentage_text is None
            else [f"📊 Процент побед: {winning_percentage_text}%"]
        ),
        "⚔️ Сейчас в игре" if is_in_game else "💤 Сейчас не в игре",
    )
    await bot.send_message(chat_id, **content.as_kwargs())


async def wait_emoji_to_buy_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Введите эмоджи")


async def not_enough_stars_to_buy_emoji_message(
    bot: Bot, chat_id: int, stars_to_become_enough: Stars,
) -> None:
    await bot.send_message(
        chat_id, f"😞 Нужно ещё {stars_to_become_enough} 🌟 для покупки",
    )


async def emoji_already_purchased_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Уже куплено")


async def invalid_emoji_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(
        chat_id, "❌ Эмоджи должен состоять из одного символа. Попробуйте ещё",
    )


async def emoji_was_purchased_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🌟 Куплено!")


async def emoji_not_purchased_to_select_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Эмоджи ещё не куплен!")


async def emoji_selected_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Эмоджи выбран")


async def selected_emoji_removed_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Эмоджи убран")


async def wait_rubles_to_start_stars_purshase_message(
    bot: Bot, chat_id: int,
) -> None:
    await bot.send_message(
        chat_id,
        "🌟 Сколько звёзд хотите купить?",
        reply_markup=stars_prices_keyboard(),
    )


async def stars_will_be_added_message(
    bot: Bot, chat_id: int,
) -> None:
    await bot.send_message(chat_id, "🌟 Звёзды скоро начислятся!")


async def stars_added_message(
    bot: Bot, chat_id: int,
) -> None:
    await bot.send_message(chat_id, "🌟 Звезды начислились!")
