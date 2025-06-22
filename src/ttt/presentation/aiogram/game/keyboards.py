from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game


def game_keyboard(game: Game) -> ReplyKeyboardMarkup:
    kb = [
        [_game_keyboard_button(cell, game) for cell in line]
        for line in game.board
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Введите позицию закрашиваемой ячейки",
    )


def _game_keyboard_button(
    cell: Cell,
    game: Game,
) -> KeyboardButton:
    match cell.filler_id:
        case game.player1.id:
            return KeyboardButton(text=game.player1_emoji.str_)
        case game.player2.id:
            return KeyboardButton(text=game.player2_emoji.str_)
        case None:
            return KeyboardButton(text=(
                f"{cell.board_position[0] + 1} {cell.board_position[1] + 1}"
            ))
        case _:
            raise ValueError((cell.filler_id, game.player1.id, game.player2.id))
