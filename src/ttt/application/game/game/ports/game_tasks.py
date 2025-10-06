from abc import ABC, abstractmethod
from uuid import UUID


class GameTasks(ABC):
    @abstractmethod
    async def make_ai_move(
        self,
        user_id: int,
        game_id: UUID,
        ai_id: UUID,
        /,
    ) -> None: ...
