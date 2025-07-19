from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game


def keyboard_to_start_game_with_ai() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="gemini 2.0 flash",
                callback_data="start_game_with_gemini_2_0_flash",
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def game_keyboard(game: Game) -> ReplyKeyboardMarkup:
    kb = [
        [_game_keyboard_button(cell, game) for cell in line]
        for line in game.board
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
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
