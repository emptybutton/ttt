from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.entities.core.game.game import Game
from ttt.entities.core.user.location import UserGameLocation, UserLocation


class GameViews(ABC):
    @abstractmethod
    async def game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def started_game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_game_view(
        self,
        user_location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_already_complteted_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_current_user_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_cell_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_filled_cell_error(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_in_game_views(
        self,
        locations: Sequence[UserLocation],
        /,
    ) -> None: ...

    @abstractmethod
    async def waiting_for_game_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def double_waiting_for_game_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...

    @abstractmethod
    async def waiting_for_ai_type_to_start_game_with_ai_view(
        self,
        location: UserLocation,
        /,
    ) -> None: ...
