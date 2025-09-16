from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game


class NoGameError(Exception): ...


class Games(ABC):
    @abstractmethod
    async def current_user_game(self, user_id: int, /) -> Game | None: ...
