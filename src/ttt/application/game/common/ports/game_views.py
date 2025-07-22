from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.entities.core.game.game import Game
from ttt.entities.core.user.location import UserGameLocation, UserLocation


class GameViews(ABC):
    @abstractmethod
    async def render_game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_started_game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_no_game_view(
        self,
        user_location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_game_already_complteted_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_not_current_user_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_no_cell_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_already_filled_cell_error(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_user_already_in_game_views(
        self,
        locations: Sequence[UserLocation],
        /,
    ) -> None: ...

    @abstractmethod
    async def render_waiting_for_game_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_double_waiting_for_game_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def render_waiting_for_ai_type_to_start_game_with_ai_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
