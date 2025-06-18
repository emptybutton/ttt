from abc import ABC, abstractmethod

from ttt.entities.core import Cell, Game, Player
from ttt.entities.tools import Tracking


class NotUniquePlayerIdError(Exception): ...


type MappableEntityLifeCycle = Tracking[Player | Game | Cell]


class Map(ABC):
    @abstractmethod
    async def __call__(
        self,
        effect: MappableEntityLifeCycle,
        /,
    ) -> None:
        """
        :raises ttt.application.common.ports.map.NotUniquePlayerIdError:
        """
