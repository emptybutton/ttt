from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game
from ttt.entities.tools.assertion import not_none


def game_cell(
    cell: Cell,
    game: Game,
    default: str,
) -> str:
    match cell.filler_id:
        case game.player1.id:
            return game.player1_emoji.str_
        case game.player2.id:
            return game.player2_emoji.str_
        case None:
            return default
        case _:
            raise ValueError((cell.filler_id, game.player1.id, game.player2.id))
