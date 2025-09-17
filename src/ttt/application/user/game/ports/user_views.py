from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game
from ttt.entities.core.user.user import User


class GameUserViews(ABC):
    @abstractmethod
    async def user_is_waiting_for_matchmaking_view(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_already_waiting_for_matchmaking_view(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_in_game_to_wait_for_matchmaking_view(
        self, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def matched_games_view(self, games: list[Game], /) -> None: ...
