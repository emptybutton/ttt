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
            return game.player1_emoji.char
        case game.player2.id:
            return game.player2_emoji.char
        case None:
            return default
        case _:
            raise ValueError((cell.filler_id, game.player1.id, game.player2.id))


def winner_emoji(game: Game) -> str:
    result = not_none(game.result)

    match result.winner_id:
        case game.player1.id:
            return game.player1_emoji.char
        case game.player2.id:
            return game.player2_emoji.char
        case None:
            return "�"
        case _:
            raise ValueError(result.winner_id)
