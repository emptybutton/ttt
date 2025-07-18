from abc import ABC, abstractmethod

from ttt.entities.atomic import Atomic
from ttt.entities.tools.tracking import Tracking


class NotUniqueUserIdError(Exception): ...


type MappableTracking = Tracking[Atomic]


class Map(ABC):
    @abstractmethod
    async def __call__(
        self,
        tracking: MappableTracking,
        /,
    ) -> None:
        """
        :raises ttt.application.common.ports.map.NotUniqueUserIdError:
        """
