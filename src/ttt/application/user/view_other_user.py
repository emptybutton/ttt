from dataclasses import dataclass

from ttt.application.common.ports.transaction import (
    ReadonlyTransaction,
)
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users


@dataclass(frozen=True, unsafe_hash=False)
class ViewOtherUser:
    views: CommonUserViews
    users: Users
    transaction: ReadonlyTransaction
    log: CommonUserLog

    async def __call__(self, user_id: int, other_user_id: int) -> None:
        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.views.user_is_not_registered_view(user_id)
                return

            if user.is_admin():
                await self.views.other_user_view(user, other_user_id)
            else:
                await self.views.user_is_not_admin_view(user)
