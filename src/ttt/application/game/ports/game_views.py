from abc import ABC, abstractmethod


class GameViews[GameViewT](ABC):
    @abstractmethod
    async def view_game_of_player_with_id(
        self, id_: int | None, /,
    ) -> GameViewT: ...
