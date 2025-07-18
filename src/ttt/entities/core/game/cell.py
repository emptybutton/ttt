from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.game.cell_number import CellNumber
from ttt.entities.math.vector import Vector
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class ManyFillersError(Exception): ...


class AlreadyFilledCellError(Exception): ...


@dataclass
class Cell:
    """
    :raises ttt.entities.core.game.cell.ManyFillersError:
    """

    id: UUID
    game_id: UUID
    board_position: Vector
    user_filler_id: int | None
    ai_filler_id: UUID | None

    def __post_init__(self) -> None:
        if self.user_filler_id is not None and self.ai_filler_id is not None:
            raise ManyFillersError

    def number(self) -> CellNumber:
        return CellNumber.of_board_position(self.board_position)

    def filler_id(self) -> int | UUID | None:
        return (
            self.user_filler_id
            if self.ai_filler_id is None
            else self.ai_filler_id
        )

    def is_filled(self) -> bool:
        return self.user_filler_id is not None or self.ai_filler_id is not None

    def is_free(self) -> bool:
        return not self.is_filled()

    def fill_as_user(self, filler_id: int, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        assert_(not self.is_filled(), else_=AlreadyFilledCellError)
        self.user_filler_id = filler_id
        tracking.register_mutated(self)

    def fill_as_ai(self, filler_id: UUID, tracking: Tracking) -> None:
        """
        :raises ttt.entities.core.game.cell.AlreadyFilledCellError:
        """

        assert_(not self.is_filled(), else_=AlreadyFilledCellError)
        self.ai_filler_id = filler_id
        tracking.register_mutated(self)
