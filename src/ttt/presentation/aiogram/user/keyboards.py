from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu_keyboard(is_user_in_game: bool) -> ReplyKeyboardMarkup:  # noqa: FBT001
    if not is_user_in_game:
        game_keyboard = [[KeyboardButton(text="Начать игру")]]
    else:
        game_keyboard = [
            [KeyboardButton(text="Вернуться к игре")],
            [KeyboardButton(text="Отменить игру")],
        ]

    keyboard = [
        *game_keyboard,
        [KeyboardButton(text="Профиль")],
        [KeyboardButton(text="Эмоджи")],
        [KeyboardButton(text="Магазин")],
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def emoji_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Выбрать эмоджи")],
        [KeyboardButton(text="Убрать эмоджи")],
        [KeyboardButton(text="Меню")],
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


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
