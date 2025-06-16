from abc import ABC, abstractmethod

from ttt.entities.time.time import Time


class Clock(ABC):
    @abstractmethod
    async def get_current_time(self) -> Time: ...
