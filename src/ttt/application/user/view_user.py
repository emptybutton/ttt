from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.entities.core.user.location import UserLocation


@dataclass(frozen=True, unsafe_hash=False)
class ViewUser:
    views: CommonUserViews
    transaction: Transaction
    log: CommonUserLog

    async def __call__(self, location: UserLocation) -> None:
        async with self.transaction:
            await self.views.render_view_of_user_with_id(location)
            await self.log.user_viewed(location)
