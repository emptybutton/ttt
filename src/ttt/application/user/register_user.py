from dataclasses import dataclass

from ttt.application.common.ports.map import Map, NotUniqueUserIdError
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_views import UserViews
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import register_user
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterUser:
    transaction: Transaction
    user_views: UserViews
    map: Map

    async def __call__(self, user_id: int, user_chat_id: int) -> None:
        location = UserLocation(user_id, user_chat_id)

        tracking = Tracking()
        register_user(user_id, tracking)

        async with self.transaction:
            try:
                await self.map(tracking)
            except NotUniqueUserIdError:
                await self.user_views.render_user_already_registered_view(
                    location,
                )
            else:
                await self.user_views.render_user_registered_view(location)
