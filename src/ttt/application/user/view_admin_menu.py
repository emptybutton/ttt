from dataclasses import dataclass

from ttt.application.common.ports.transaction import ReadonlyTransaction, SerializableTransaction
from ttt.application.user.common.ports.user_views import CommonUserViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewAdminMenu:
    views: CommonUserViews
    transaction: ReadonlyTransaction

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            return await self.views.user_admin_view(user_id)
