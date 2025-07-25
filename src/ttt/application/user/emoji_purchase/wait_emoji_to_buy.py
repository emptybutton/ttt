from asyncio import gather
from dataclasses import dataclass

from ttt.application.user.common.ports.user_fsm import (
    UserFsm,
    WaitingEmojiToBuyState,
)
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.application.user.emoji_purchase.ports.user_views import (
    EmojiPurchaseUserViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class WaitEmojiToBuy:
    fsm: UserFsm
    user_views: EmojiPurchaseUserViews
    log: EmojiPurchaseUserLog

    async def __call__(self, user_id: int) -> None:
        await gather(
            self.fsm.set(WaitingEmojiToBuyState()),
            self.user_views.wait_emoji_to_buy_view(user_id),
        )
        await self.log.user_intends_to_buy_emoji(user_id)
