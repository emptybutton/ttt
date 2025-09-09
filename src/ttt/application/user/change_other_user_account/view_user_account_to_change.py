from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.change_other_user_account.ports.user_views import (
    ChangeOtherUserAccountViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class ViewUserAccountToChange:
    transaction: Transaction
    views: ChangeOtherUserAccountViews

    async def __call__(
        self, user_id: int, other_user_id: int,
    ) -> None:
        async with self.transaction:
            await self.views.user_account_to_change_view(
                user_id, other_user_id,
            )
