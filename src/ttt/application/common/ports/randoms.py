from abc import ABC, abstractmethod

from ttt.entities.math.random import Random


class Randoms(ABC):
    @abstractmethod
    async def random(self) -> Random: ...
