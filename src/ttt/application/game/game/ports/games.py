from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.game.game import Game


class NoGameError(Exception): ...


class Games(ABC):
    @abstractmethod
    async def current_user_game(self, user_id: int, /) -> Game | None: ...

    @abstractmethod
    async def not_locked_game_with_id(self, game_id: UUID, /) -> Game | None:
        ...
