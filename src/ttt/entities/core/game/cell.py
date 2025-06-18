from dataclasses import dataclass
from uuid import UUID

from ttt.entities.math.vector import Vector
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class AlreadyFilledCellError(Exception): ...


@dataclass
class Cell:
    id: UUID
    game_id: UUID
    board_position: Vector
    filler_id: int | None

    def is_filled(self) -> bool:
        return self.filler_id is not None

    def fill(self, filler_id: int, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        assert_(not self.is_filled(), else_=AlreadyFilledCellError)
        self.filler_id = filler_id
        tracking.register_mutated(self)
