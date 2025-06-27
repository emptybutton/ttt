from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import overload

from ttt.entities.core.player.player import Player


@dataclass(frozen=True)
class NoPlayerWithIDError(Exception):
    player_id: int


class Players(ABC):
    @abstractmethod
    async def contains_player_with_id(
        self, id_: int, /,
    ) -> bool:
        ...

    @abstractmethod
    async def player_with_id(self, id_: int, /) -> Player: ...

    @abstractmethod
    @overload
    async def players_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[Player, ...]: ...

    @abstractmethod
    @overload
    async def players_with_ids(  # type: ignore[overload-cannot-match]
        self, ids: tuple[int, int], /,
    ) -> tuple[Player, Player]: ...

    @abstractmethod
    async def players_with_ids(
        self, ids: Sequence[int], /,
    ) -> tuple[Player, ...]:
        """
        :raises ttt.application.player.ports.players.NoPlayerWithIDError:
        """
