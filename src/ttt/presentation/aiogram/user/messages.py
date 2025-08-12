from collections.abc import Sequence

from aiogram import Bot
from aiogram.utils.formatting import (
    Bold,
    Italic,
    Text,
    Underline,
    as_list,
)

from ttt.entities.core.stars import Stars
from ttt.presentation.aiogram.common.texts import short_float_text
from ttt.presentation.aiogram.user.keyboards import (
    emoji_menu_keyboard,
    main_menu_keyboard,
    stars_prices_keyboard,
)
from ttt.presentation.aiogram.user.texts import emoji_list_text


async def profile_message(  # noqa: PLR0913, PLR0917
    bot: Bot,
    chat_id: int,
    stars: int,
    rating: float,
    number_of_wins: int,
    number_of_draws: int,
    number_of_defeats: int,
) -> None:
    content = as_list(
        f"🌟 Звёзд: {stars}",
        f"🏅 Рейтинг: {short_float_text(rating)}",
        f"🏆 Побед: {number_of_wins}",
        f"💀 Поражений: {number_of_defeats}",
        f"🕊️ Ничьих: {number_of_draws}",
    )
    await bot.send_message(chat_id, **content.as_kwargs())


async def emoji_menu_message(
    bot: Bot,
    chat_id: int,
    emojis: Sequence[str],
    selected_emoji: str | None,
) -> None:
    emoji_list_text_ = emoji_list_text(emojis, selected_emoji)

    if emoji_list_text_ is not None:
        keyboard = emoji_menu_keyboard()
        await bot.send_message(
            chat_id, **emoji_list_text_.as_kwargs(), reply_markup=keyboard,
        )
    else:
        emoji_text = Text("🎭 У вас нет купленных эмоджи")
        await bot.send_message(chat_id, **emoji_text.as_kwargs())


async def emoji_list_message(
    bot: Bot,
    chat_id: int,
    emojis: Sequence[str],
    selected_emoji: str | None,
) -> None:
    emoji_list_text_ = emoji_list_text(emojis, selected_emoji)

    if emoji_list_text_ is not None:
        await bot.send_message(chat_id, **emoji_list_text_.as_kwargs())
    else:
        emoji_text = Text("🎭 У вас нет купленных эмоджи")
        await bot.send_message(chat_id, **emoji_text.as_kwargs())


async def wait_emoji_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Введите эмоджи")


async def not_enough_stars_to_buy_emoji_message(
    bot: Bot,
    chat_id: int,
    stars_to_become_enough: Stars,
) -> None:
    await bot.send_message(
        chat_id,
        f"😞 Нужно ещё {stars_to_become_enough} 🌟 для покупки",
    )


async def emoji_already_purchased_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Уже куплено")


async def invalid_emoji_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(
        chat_id,
        "❌ Эмоджи должен состоять из одного символа. Попробуйте ещё",
    )


async def emoji_was_purchased_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🌟 Куплено!")


async def emoji_not_purchased_to_select_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Эмоджи ещё не куплен!")


async def selected_emoji_removed_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "🎭 Эмоджи убран")


async def wait_stars_to_start_stars_purchase_message(
    bot: Bot,
    chat_id: int,
) -> None:
    await bot.send_message(
        chat_id,
        "🌟 Сколько звёзд хотите купить?",
        reply_markup=stars_prices_keyboard(),
    )


async def stars_will_be_added_message(
    bot: Bot,
    chat_id: int,
) -> None:
    await bot.send_message(chat_id, "🌟 Звёзды скоро начислятся!")


async def stars_added_message(
    bot: Bot,
    chat_id: int,
) -> None:
    await bot.send_message(chat_id, "🌟 Звезды начислились!")


async def welcome_message(
    bot: Bot, chat_id: int, is_user_in_game: bool,  # noqa: FBT001
) -> None:
    description = Text(
        Underline(Italic(Bold("ttt!"))),
        " — многопользовательские онлайн-крестики-нолики в Telegram.",
    )

    await bot.send_message(
        chat_id,
        reply_markup=main_menu_keyboard(is_user_in_game),
        **description.as_kwargs(),
    )


async def menu_message(bot: Bot, chat_id: int, is_user_in_game: bool) -> None:  # noqa: FBT001
    text = "🧭 Выбери свой путь"

    await bot.send_message(
        chat_id,
        text=text,
        reply_markup=main_menu_keyboard(is_user_in_game),
    )
