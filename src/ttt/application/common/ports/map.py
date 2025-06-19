from abc import ABC, abstractmethod

from ttt.entities.aggregate import Aggregate
from ttt.entities.tools.tracking import Tracking


class NotUniquePlayerIdError(Exception): ...


type MappableTracking = Tracking[Aggregate]


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
