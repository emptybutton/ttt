from abc import ABC, abstractmethod


class Retry(ABC):
    @abstractmethod
    def __bool__(self) -> bool: ...
