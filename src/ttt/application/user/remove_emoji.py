from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.location import UserLocation
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RemoveEmoji:
    transaction: Transaction
    users: Users
    user_views: UserViews
    map_: Map

    async def __call__(self, location: UserLocation) -> None:
        async with self.transaction:
            user = await self.users.user_with_id(location.user_id)

            if user is None:
                await self.user_views.render_user_is_not_registered_view(
                    location,
                )
                return

            tracking = Tracking()
            user.remove_selected_emoji(tracking)

            await self.map_(tracking)
            await self.user_views.render_selected_emoji_removed_view(location)
