from abc import ABC, abstractmethod

from ttt.entities.core import Cell, Game, Player
from ttt.entities.tools import Tracking


type MappableEntityLifeCycle = Tracking[Player | Cell | Game]


class NotUniqueUserNameError(Exception): ...


class Map(ABC):
    @abstractmethod
    async def __call__(
        self,
        effect: MappableEntityLifeCycle,
        /,
    ) -> None:
        """
        :raises ttt.application.ports.map.NotUniqueUserNameError:
        """
