from abc import ABC, abstractmethod

from ttt.entities.core.player.location import PlayerLocation


class PlayerViews(ABC):
    @abstractmethod
    async def render_view_of_player_with_id(self, player_id: int, /) -> None:
        ...

    @abstractmethod
    async def render_player_is_not_registered_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_player_already_registered_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_player_registered_view(
        self, location: PlayerLocation, /,
    ) -> None: ...
