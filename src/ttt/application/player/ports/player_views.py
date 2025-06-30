from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.player import Player
from ttt.entities.core.stars import Stars


class PlayerViews(ABC):
    @abstractmethod
    async def render_view_of_player_with_id(
        self, location: PlayerLocation, /,
    ) -> None:
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

    @abstractmethod
    async def render_wait_rubles_to_start_stars_purshase_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_non_exchangeable_rubles_for_stars_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_stars_purchase_will_be_completed_view(
        self, location: PlayerLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_completed_stars_purshase_view(
        self, player: Player, purshase_id: UUID, location: PlayerLocation, /,
    ) -> None: ...
