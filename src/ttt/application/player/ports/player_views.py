from abc import ABC, abstractmethod

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.stars import Stars


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

    @abstractmethod
    async def render_wait_emoji_to_buy_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_not_enough_stars_to_buy_emoji_view(
        self, location: PlayerLocation, stars_to_become_enough: Stars, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_already_purchased_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_was_purchased_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_invalid_emoji_to_buy_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_invalid_emoji_to_select_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_not_purchased_to_select_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_selected_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_selected_emoji_removed_view(
        self, location: PlayerLocation, /,
    ) -> None: ...
