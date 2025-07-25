from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.user.common.ports.user_fsm import (
    UserFsm,
    WaitingEmojiToBuyState,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.application.user.emoji_purchase.ports.user_views import (
    EmojiPurchaseUserViews,
)
from ttt.entities.core.user.user import (
    EmojiAlreadyPurchasedError,
    NotEnoughStarsError,
)
from ttt.entities.text.emoji import Emoji, InvalidEmojiError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class BuyEmoji:
    fsm: UserFsm
    uuids: UUIDs
    clock: Clock
    transaction: Transaction
    users: Users
    common_views: CommonUserViews
    emoji_purchase_views: EmojiPurchaseUserViews
    map_: Map
    log: EmojiPurchaseUserLog

    async def __call__(
        self,
        user_id: int,
        emoji_str: str | None,
    ) -> None:
        await self.fsm.state(WaitingEmojiToBuyState)

        if emoji_str is None:
            await self.emoji_purchase_views.invalid_emoji_to_buy_view(user_id)
            return

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await self.emoji_purchase_views.invalid_emoji_to_buy_view(user_id)
            return

        purchased_emoji_id, current_datetime = await gather(
            self.uuids.random_uuid(),
            self.clock.current_datetime(),
        )

        async with self.transaction:
            user = await self.users.user_with_id(user_id)

            if user is None:
                await self.common_views.user_is_not_registered_view(user_id)
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                user.buy_emoji(
                    emoji,
                    purchased_emoji_id,
                    tracking,
                    current_datetime,
                )
            except EmojiAlreadyPurchasedError:
                await self.log.emoji_already_purchased_to_buy(user, emoji)
                await self.fsm.set(None)
                await self.emoji_purchase_views.emoji_already_purchased_view(
                    user_id,
                )
            except NotEnoughStarsError as error:
                await self.fsm.set(None)
                await (
                    self.emoji_purchase_views
                    .not_enough_stars_to_buy_emoji_view(
                        user_id,
                        error.stars_to_become_enough,
                    )
                )
            else:
                await self.log.user_bought_emoji(user, emoji)

                await self.map_(tracking)
                await self.fsm.set(None)
                await self.emoji_purchase_views.emoji_was_purchased_view(
                    user_id,
                )
