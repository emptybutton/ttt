from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload

from ttt.entities.core.user.rank import UsersWithMaxRating
from ttt.entities.core.user.user import User
from ttt.entities.elo.rating import EloRating


class Users(ABC):
    @abstractmethod
    async def contains_user_with_id(
        self,
        id_: int,
        /,
    ) -> bool: ...

    @abstractmethod
    async def user_with_id(self, id_: int, /) -> User | None: ...

    @abstractmethod
    @overload
    async def users_with_ids(
        self,
        ids: Sequence[int],
        /,
    ) -> tuple[User | None, ...]: ...

    @abstractmethod
    @overload
    async def users_with_ids(  # type: ignore[overload-cannot-match]
        self,
        ids: tuple[int, int],
        /,
    ) -> tuple[User | None, User | None]: ...

    @abstractmethod
    async def users_with_ids(
        self,
        ids: Sequence[int],
        /,
    ) -> tuple[User | None, ...]: ...

    @abstractmethod
    async def some_users_waiting_for_matchmaking_to_matchmake(
        self,
    ) -> list[User]: ...

    @abstractmethod
    async def max_rating_and_users_with_max_rating(
        self,
    ) -> tuple[EloRating, UsersWithMaxRating]: ...
