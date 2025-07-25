from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RemoveEmoji:
    transaction: Transaction
    users: Users
    views: CommonUserViews
    map_: Map
    log: CommonUserLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.views.user_is_not_registered_view(user_id)
                return

            tracking = Tracking()
            user.remove_selected_emoji(tracking)
            await self.log.user_removed_emoji(user_id, user)

            await self.map_(tracking)
            await self.views.selected_emoji_removed_view(user_id)
