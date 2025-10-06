from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)
from ttt.entities.core.user.user import EmojiNotPurchasedError
from ttt.entities.text.emoji import Emoji, InvalidEmojiError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class SelectEmoji:
    transaction: SerializableTransaction
    users: Users
    user_views: CommonUserViews
    emoji_selection_views: EmojiSelectionUserViews
    map_: Map
    log: EmojiSelectionUserLog

    async def __call__(
        self,
        user_id: int,
        emoji_str: str,
    ) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await (
                self.emoji_selection_views
                .invalid_emoji_to_select_view(user_id)
            )
            return

        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.transaction.commit()
                await self.user_views.user_is_not_registered_view(user_id)
                return

            tracking = Tracking()
            try:
                user.select_emoji(emoji, tracking)
            except EmojiNotPurchasedError:
                await self.log.emoji_not_purchased_to_select(user, emoji)
                await self.transaction.commit()
                await (
                    self.emoji_selection_views
                    .emoji_not_purchased_to_select_view(user_id)
                )
            else:
                await self.log.user_selected_emoji(user, emoji)
                await self.map_(tracking)
                await self.transaction.commit()
