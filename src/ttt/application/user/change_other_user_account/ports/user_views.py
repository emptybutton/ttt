from abc import ABC, abstractmethod

from ttt.entities.core.stars import Stars
from ttt.entities.core.user.user import User


class ChangeOtherUserAccountViews(ABC):
    @abstractmethod
    async def user_account_to_change_view(
        self, user_id: int, other_user_id: int, /,
    ) -> None: ...

    @abstractmethod
    async def negative_account_on_change_other_user_account_view(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None: ...

    @abstractmethod
    async def negative_account_on_set_other_user_account_view(
        self,
        user: User,
        other_user: User | None,
        other_user_id: int,
        other_user_account_stars: Stars,
        /,
    ) -> None: ...

    @abstractmethod
    async def user_set_other_user_account_view(
        self, user: User, other_user: User, /,
    ) -> None: ...

    @abstractmethod
    async def user_changed_other_user_account_view(
        self,
        user: User,
        other_user: User,
        other_user_account_stars_vector: Stars,
        /,
    ) -> None: ...
