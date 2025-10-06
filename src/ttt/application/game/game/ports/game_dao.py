from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game
from ttt.entities.elo.rating import GamesPlayed


class GameDao(ABC):
    @abstractmethod
    async def games_played_by_player_id(
        self,
        game: Game,
        /,
    ) -> dict[int, GamesPlayed]: ...
