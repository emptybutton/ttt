from abc import ABC, abstractmethod
from uuid import UUID

from ttt.entities.core.stars import Stars
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import User


class UserViews(ABC):
    @abstractmethod
    async def render_view_of_user_with_id(
        self, location: UserLocation, /,
    ) -> None:
        ...

    @abstractmethod
    async def render_user_is_not_registered_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_user_already_registered_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_user_registered_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_wait_emoji_to_buy_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_not_enough_stars_to_buy_emoji_view(
        self, location: UserLocation, stars_to_become_enough: Stars, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_already_purchased_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_was_purchased_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_invalid_emoji_to_buy_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_invalid_emoji_to_select_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_not_purchased_to_select_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_emoji_selected_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_selected_emoji_removed_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_wait_stars_to_start_stars_purshase_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_invalid_stars_for_stars_purchase_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_stars_purchase_will_be_completed_view(
        self, location: UserLocation, /,
    ) -> None: ...

    @abstractmethod
    async def render_completed_stars_purshase_view(
        self, user: User, purshase_id: UUID, location: UserLocation, /,
    ) -> None: ...
