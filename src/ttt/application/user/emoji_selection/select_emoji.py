from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.user.common.ports.user_fsm import (
    UserFsm,
    WaitingEmojiToSelectState,
)
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import EmojiNotPurchasedError
from ttt.entities.text.emoji import Emoji, InvalidEmojiError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class SelectEmoji:
    fsm: UserFsm
    transaction: Transaction
    users: Users
    user_views: UserViews
    map_: Map

    async def __call__(
        self, location: UserLocation, emoji_str: str | None,
    ) -> None:
        await self.fsm.state(WaitingEmojiToSelectState)

        if emoji_str is None:
            await self.user_views.render_invalid_emoji_to_select_view(
                location,
            )
            return

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await self.user_views.render_invalid_emoji_to_select_view(
                location,
            )
            return

        async with self.transaction:
            user = await self.users.user_with_id(location.user_id)

            if user is None:
                await self.user_views.render_user_is_not_registered_view(
                    location,
                )
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                user.select_emoji(emoji, tracking)
            except EmojiNotPurchasedError:
                await self.fsm.set(None)
                await (
                    self.user_views
                    .render_emoji_not_purchased_to_select_view(location)
                )
            else:
                await self.map_(tracking)
                await self.fsm.set(None)
                await self.user_views.render_emoji_selected_view(location)
