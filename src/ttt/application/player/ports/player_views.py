from abc import ABC, abstractmethod


class PlayerViews[PlayerWithIDViewT](ABC):
    @abstractmethod
    async def view_of_player_with_id(
        self, player_id: int, /,
    ) -> PlayerWithIDViewT: ...
