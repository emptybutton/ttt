from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def stars_prices_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="8192 🌟 (128₽)",
                callback_data="128_rub_for_stars",
            ),
            InlineKeyboardButton(
                text="16384 🌟 (256₽)",
                callback_data="256_rub_for_stars",
            ),
        ],
        [
            InlineKeyboardButton(
                text="32768 🌟 (512₽)",
                callback_data="512_rub_for_stars",
            ),
            InlineKeyboardButton(
                text="65536 🌟 (1024₽)",
                callback_data="1024_rub_for_stars",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
