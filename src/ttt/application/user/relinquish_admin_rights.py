from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.user import NotAdminError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RelinquishAdminRights:
    transaction: Transaction
    users: Users
    map_: Map
    log: CommonUserLog
    views: CommonUserViews

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.views.user_is_not_registered_view(user_id)
                return

            try:
                tracking = Tracking()
                user.relinquish_admin_rights(tracking)
            except NotAdminError:
                await self.log.not_admin_to_relinquish_admin_rights(user)
                await self.views.not_admin_to_relinquish_admin_rights_view(user)
            else:
                await self.log.user_relinquished_admin_rights(user)
                await self.map_(tracking)
                await self.views.user_relinquished_admin_rights_view(user)
