from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def stars_prices_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="256 🌟 (8₽)",
                callback_data="8_rub_for_stars",
            ),
            InlineKeyboardButton(
                text="2048 🌟 (64₽)",
                callback_data="64_rub_for_stars",
            ),
            InlineKeyboardButton(
                text="4096 🌟 (128₽)",
                callback_data="128_rub_for_stars",
            ),
        ],
        [
            InlineKeyboardButton(
                text="131072 🌟 (1024₽)",
                callback_data="1024_rub_for_stars",
            ),
            InlineKeyboardButton(
                text="32768 🌟 (512₽)",
                callback_data="512_rub_for_stars",
            ),
            InlineKeyboardButton(
                text="10240 🌟 (256₽)",
                callback_data="256_rub_for_stars",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
