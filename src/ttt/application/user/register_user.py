from dataclasses import dataclass

from ttt.application.common.ports.map import Map, NotUniqueUserIdError
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.entities.core.user.user import register_user
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterUser:
    transaction: Transaction
    views: CommonUserViews
    map_: Map
    log: CommonUserLog

    async def __call__(self, user_id: int) -> None:
        tracking = Tracking()
        user = register_user(user_id, tracking)

        async with self.transaction:
            try:
                await self.map_(tracking)
            except NotUniqueUserIdError:
                await self.log.user_double_registration(user_id, user)
                await self.views.user_already_registered_view(user_id)
            else:
                await self.log.user_registered(user_id, user)
                await self.views.user_registered_view(user_id)
