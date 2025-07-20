from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import UserViews
from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True, unsafe_hash=False)
class ViewUser:
    user_views: UserViews
    transaction: Transaction
    log: CommonUserLog

    async def __call__(self, location: UserLocation) -> None:
        async with self.transaction:
            await self.user_views.render_view_of_user_with_id(location)
            await self.log.user_viewed(location)
