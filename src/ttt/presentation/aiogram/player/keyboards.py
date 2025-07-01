from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def stars_prices_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="8192 🌟 (128₽)",
                callback_data="8192_stars_purchase",
            ),
            InlineKeyboardButton(
                text="16384 🌟 (256₽)",
                callback_data="16384_stars_purchase",
            ),
        ],
        [
            InlineKeyboardButton(
                text="32768 🌟 (512₽)",
                callback_data="32768_stars_purchase",
            ),
            InlineKeyboardButton(
                text="65536 🌟 (1024₽)",
                callback_data="65536_stars_purchase",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
