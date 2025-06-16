from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.user import User


class Users(ABC):
    @abstractmethod
    async def user_with_id(self, id_: UUID, /) -> User | None: ...
