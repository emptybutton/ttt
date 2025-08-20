from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.game.cell_number import CellNumber


@dataclass(frozen=True)
class UserMove:
    next_move_ai_id: UUID | None
    filled_cell_number: CellNumber


@dataclass(frozen=True)
class AiMove:
    was_random: bool
    filled_cell_number: CellNumber


type Move = UserMove | AiMove
