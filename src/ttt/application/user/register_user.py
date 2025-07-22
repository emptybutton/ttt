from dataclasses import dataclass

from ttt.application.common.ports.map import Map, NotUniqueUserIdError
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import register_user
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterUser:
    transaction: Transaction
    views: CommonUserViews
    map_: Map
    log: CommonUserLog

    async def __call__(self, user_id: int, user_chat_id: int) -> None:
        location = UserLocation(user_id, user_chat_id)

        tracking = Tracking()
        user = register_user(user_id, tracking)

        async with self.transaction:
            try:
                await self.map_(tracking)
            except NotUniqueUserIdError:
                await self.log.user_double_registration(location, user)
                await self.views.render_user_already_registered_view(location)
            else:
                await self.log.user_registered(location, user)
                await self.views.render_user_registered_view(location)
