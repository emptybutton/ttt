from abc import ABC, abstractmethod

from ttt.entities.core.game.game import Game
from ttt.entities.core.user.user import User


class GameUserLog(ABC):
    @abstractmethod
    async def user_is_waiting_for_matchmaking(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_not_waiting_for_matchmaking(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_already_waiting_for_matchmaking(
        self,
        user: User,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_is_in_game_to_wait_for_matchmaking(
        self, user: User, /,
    ) -> None: ...

    @abstractmethod
    async def games_were_matched(self, games: list[Game], /) -> None: ...

    @abstractmethod
    async def user_is_not_waiting_for_matchmaking_to_dont_wait(
        self, user: User, /,
    ) -> None: ...
