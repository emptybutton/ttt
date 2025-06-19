from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game


class GameViews[GameViewT](ABC):
    @abstractmethod
    async def render_game_view_for_players_with_ids(
        self,
        player_ids: tuple[int, ...],
        game: Game,
        /,
    ) -> GameViewT: ...
