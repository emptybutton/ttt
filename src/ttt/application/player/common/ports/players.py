from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload

from ttt.entities.core.player.player import Player


class Players(ABC):
    @abstractmethod
    async def contains_player_with_id(
        self, id_: int, /,
    ) -> bool:
        ...

    @abstractmethod
    async def player_with_id(self, id_: int, /) -> Player | None: ...

    @abstractmethod
    @overload
    async def players_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[Player | None, ...]: ...

    @abstractmethod
    @overload
    async def players_with_ids(  # type: ignore[overload-cannot-match]
        self, ids: tuple[int, int], /,
    ) -> tuple[Player | None, Player | None]: ...

    @abstractmethod
    async def players_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[Player | None, ...]: ...
