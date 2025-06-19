from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.entities.core.game.game import Game
from ttt.entities.core.player.location import JustLocation


class GameViews(ABC):
    @abstractmethod
    async def render_game_view_for_players_with_locations(
        self,
        player_locations: Sequence[JustLocation],
        game: Game,
        /,
    ) -> None: ...
