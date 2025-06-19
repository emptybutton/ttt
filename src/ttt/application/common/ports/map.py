from abc import ABC, abstractmethod

from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game
from ttt.entities.core.player.player import Player
from ttt.entities.tools.tracking import Tracking


class NotUniquePlayerIdError(Exception): ...


type MappableTracking = Tracking[Player | Game | Cell]


class Map(ABC):
    @abstractmethod
    async def __call__(
        self,
        tracking: MappableTracking,
        /,
    ) -> None:
        """
        :raises ttt.application.common.ports.map.NotUniquePlayerIdError:
        """
