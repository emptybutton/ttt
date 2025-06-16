from abc import ABC, abstractmethod

from effect import LifeCycle

from ttt.entities.core.user import User


type MappableEntityLifeCycle = LifeCycle[User]


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
        """  # noqa: E501
