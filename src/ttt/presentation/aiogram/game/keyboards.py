from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game


def keyboard_to_select_game_mode() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="👥 Против человека",
                callback_data="game_mode_against_user_to_start_game",
            ),
            InlineKeyboardButton(
                text="🤖 Против ИИ",
                callback_data=(
                    "game_mode_against_ai_to_wait_ai_type_to_start_game"
                ),
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def keyboard_to_start_game_with_ai() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="gemini 2.0 flash",
                callback_data="start_game_with_gemini_2_0_flash",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def game_keyboard(game: Game) -> ReplyKeyboardMarkup:
    board_keyboard = [
        [_game_keyboard_button(cell, game) for cell in line]
        for line in game.board
    ]
    keyboard = [
        *board_keyboard,
        [KeyboardButton(text="Меню")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        input_field_placeholder="Введите номер закрашиваемой ячейки",
    )


def _game_keyboard_button(
    cell: Cell,
    game: Game,
) -> KeyboardButton:
    match cell.filler_id():
        case game.player1.id:
            return KeyboardButton(text=game.player1_emoji.str_)
        case game.player2.id:
            return KeyboardButton(text=game.player2_emoji.str_)
        case None:
            return KeyboardButton(text=f"{int(cell.number())}")
        case _:
            raise ValueError((cell.filler_id, game.player1.id, game.player2.id))
