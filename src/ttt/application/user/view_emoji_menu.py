from dataclasses import dataclass

from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.user_views import CommonUserViews


@dataclass(frozen=True, unsafe_hash=False)
class ViewEmojiMenu:
    views: CommonUserViews
    transaction: Transaction
    log: CommonUserLog

    async def __call__(self, user_id: int) -> None:
        async with self.transaction:
            await self.views.emoji_menu_view(user_id)
            await self.log.emoji_menu_viewed(user_id)
