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
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.entities.core.user.location import UserLocation
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
    user_views: UserViews
    map_: Map
    log: EmojiPurchaseUserLog

    async def __call__(
        self, location: UserLocation, emoji_str: str | None,
    ) -> None:
        await self.fsm.state(WaitingEmojiToBuyState)

        if emoji_str is None:
            await self.user_views.render_invalid_emoji_to_buy_view(location)
            return

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await self.user_views.render_invalid_emoji_to_buy_view(location)
            return

        purchased_emoji_id, current_datetime = await gather(
            self.uuids.random_uuid(),
            self.clock.current_datetime(),
        )

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
                user.buy_emoji(
                    emoji, purchased_emoji_id, tracking, current_datetime,
                )
            except EmojiAlreadyPurchasedError:
                await self.log.emoji_already_purchased_to_buy(user, location, emoji)
                await self.fsm.set(None)
                await self.user_views.render_emoji_already_purchased_view(
                    location,
                )
            except NotEnoughStarsError as error:
                await self.fsm.set(None)
                await (
                    self.user_views
                    .render_not_enough_stars_to_buy_emoji_view(
                        location, error.stars_to_become_enough,
                    )
                )
            else:
                await self.log.user_bought_emoji(location, user, emoji)

                await self.map_(tracking)
                await self.fsm.set(None)
                await self.user_views.render_emoji_was_purchased_view(
                    location,
                )
