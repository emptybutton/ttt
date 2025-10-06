from abc import ABC, abstractmethod


class UserLocks(ABC):
    @abstractmethod
    async def lock_user_by_id(
        self,
        user_id: int,
        /,
    ) -> None: ...
