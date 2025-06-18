from abc import ABC, abstractmethod
from dataclasses import dataclass

from ttt.entities.core.player import Player


@dataclass(frozen=True)
class NoPlayerError(Exception):
    player_id: int


class Players(ABC):
    @abstractmethod
    async def assert_contains_player_with_id(self, id_: int, /) -> None:
        """
        :raises ttt.application.common.ports.players.NoPlayerError:
        """

    @abstractmethod
    async def player_with_id(self, id_: int, /) -> Player:
        """
        :raises ttt.application.common.ports.players.NoPlayerError:
        """

    @abstractmethod
    async def players_with_id(
        self, id1: int, id2: int, /,
    ) -> tuple[Player, Player]:
        """
        :raises ttt.application.common.ports.players.NoPlayerError:
        """
