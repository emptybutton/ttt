from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game


class GameViews(ABC):
    @abstractmethod
    async def current_game_view_with_user_id(self, user_id: int, /) -> None: ...

    @abstractmethod
    async def game_view(self, game: Game, /) -> None: ...

    @abstractmethod
    async def started_game_view(
        self,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_current_game_view(
        self,
        user_id: int,
        /,
    ) -> None: ...

    @abstractmethod
    async def game_already_complteted_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def not_current_user_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def no_cell_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def already_filled_cell_error(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_already_in_game_view(self, user_id: int, /) -> None: ...
