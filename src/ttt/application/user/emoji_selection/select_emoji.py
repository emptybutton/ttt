from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_fsm import (
    UserFsm,
    WaitingEmojiToSelectState,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import EmojiNotPurchasedError
from ttt.entities.text.emoji import Emoji, InvalidEmojiError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class SelectEmoji:
    fsm: UserFsm
    transaction: Transaction
    users: Users
    user_views: CommonUserViews
    emoji_selection_views: EmojiSelectionUserViews
    map_: Map
    log: EmojiSelectionUserLog

    async def __call__(
        self,
        location: UserLocation,
        emoji_str: str | None,
    ) -> None:
        await self.fsm.state(WaitingEmojiToSelectState)

        if emoji_str is None:
            await self.emoji_selection_views.invalid_emoji_to_select_view(
                location,
            )
            return

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await (
                self.emoji_selection_views
                .invalid_emoji_to_select_view(location)
            )
            return

        async with self.transaction:
            user = await self.users.user_with_id(location.user_id)

            if user is None:
                await self.user_views.user_is_not_registered_view(location)
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                user.select_emoji(emoji, tracking)
            except EmojiNotPurchasedError:
                await self.log.emoji_not_purchased_to_select(
                    location,
                    user,
                    emoji,
                )
                await self.fsm.set(None)
                await (
                    self.emoji_selection_views
                    .emoji_not_purchased_to_select_view(location)
                )
            else:
                await self.log.user_selected_emoji(location, user, emoji)

                await self.map_(tracking)
                await self.fsm.set(None)
                await self.emoji_selection_views.emoji_selected_view(location)
