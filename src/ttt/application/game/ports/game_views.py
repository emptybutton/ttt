from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.entities.core.game.game import Game
from ttt.entities.core.player.location import GameLocation


class GameViews(ABC):
    @abstractmethod
    async def render_game_view_with_locations(
        self,
        player_locations: Sequence[GameLocation],
        game: Game,
        /,
    ) -> None: ...
