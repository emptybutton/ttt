from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    @abstractmethod
    async def current_datetime(self) -> datetime: ...
