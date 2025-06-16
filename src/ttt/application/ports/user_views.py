from abc import ABC, abstractmethod


class UserViews[UserWithIDViewT](ABC):
    @abstractmethod
    async def view_of_user_with_id(self, user_id: int, /) -> UserWithIDViewT:
        ...
