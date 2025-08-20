from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_views import CommonUserViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewUserEmojis:
    views: CommonUserViews
    transaction: Transaction

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            return await self.views.view_of_user_emojis_with_id(user_id)
