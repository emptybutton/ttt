from asyncio import gather
from dataclasses import dataclass

from ttt.application.user.common.ports.user_fsm import (
    UserFsm,
    WaitingEmojiToSelectState,
)
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)


@dataclass(frozen=True, unsafe_hash=False)
class WaitEmojiToSelect:
    fsm: UserFsm
    views: EmojiSelectionUserViews
    log: EmojiSelectionUserLog

    async def __call__(self, user_id: int) -> None:
        await gather(
            self.fsm.set(WaitingEmojiToSelectState()),
            self.views.wait_emoji_to_select_view(user_id),
        )
        await self.log.user_intends_to_select_emoji(user_id)
