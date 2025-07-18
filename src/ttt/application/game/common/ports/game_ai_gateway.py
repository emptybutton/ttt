from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.game.game import Game


class GameAiGateway(ABC):
    @abstractmethod
    async def next_move_cell_number_int(
        self, game: Game, ai_id: UUID, /,
    ) -> int | None: ...
