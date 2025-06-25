from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.game.game import Game


class NoGameError(Exception): ...


class Games(ABC):
    @abstractmethod
    async def game_with_id(self, id_: UUID | None, /) -> Game:
        """
        :raises ttt.application.game.ports.games.NoGameError:
        """

    @abstractmethod
    async def game_with_game_location(
        self, game_location_player_id: int, /,
    ) -> Game | None: ...
