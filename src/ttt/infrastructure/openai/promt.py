from uuid import UUID

from ttt.entities.core.game.game import Game
from ttt.entities.math.vector import Vector


type Promt = str


def next_move_cell_number_promt(game: Game, ai_id: UUID) -> Promt:
    line1, line2, line3 = (
        "".join(
            _next_move_cell_number_promt_cell(game, ai_id, (x, y))
            for x in range(3)
        )
        for y in range(3)
    )

    return f"""
You are a tic-tac-toe user.
You play for 1, the enemy for 0, _ - empty cells.
Each number is a position on the board:
123
456
789

What position will your move be if the board is:
{line1}
{line2}
{line3}

Return only the position number
"""


def _next_move_cell_number_promt_cell(
    game: Game,
    ai_id: UUID,
    cell_position: Vector,
) -> str:
    cell = game.board[cell_position]
    filler_id = cell.filler_id()

    if filler_id == ai_id:
        return "1"
    if filler_id is None:
        return "_"

    return "0"
