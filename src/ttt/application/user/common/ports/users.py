from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload

from ttt.entities.core.user.user import User


class Users(ABC):
    @abstractmethod
    async def contains_user_with_id(
        self, id_: int, /,
    ) -> bool:
        ...

    @abstractmethod
    async def user_with_id(self, id_: int, /) -> User | None: ...

    @abstractmethod
    @overload
    async def users_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[User | None, ...]: ...

    @abstractmethod
    @overload
    async def users_with_ids(  # type: ignore[overload-cannot-match]
        self, ids: tuple[int, int], /,
    ) -> tuple[User | None, User | None]: ...

    @abstractmethod
    async def users_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[User | None, ...]: ...
