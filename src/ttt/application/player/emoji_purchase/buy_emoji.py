from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.player.common.ports.player_fsm import (
    PlayerFsm,
    WaitingEmojiToBuyState,
)
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.application.player.common.ports.players import Players
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.player import (
    EmojiAlreadyPurchasedError,
    NotEnoughStarsError,
)
from ttt.entities.text.emoji import Emoji, InvalidEmojiError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class BuyEmoji:
    fsm: PlayerFsm
    uuids: UUIDs
    clock: Clock
    transaction: Transaction
    players: Players
    player_views: PlayerViews
    map_: Map

    async def __call__(
        self, location: PlayerLocation, emoji_str: str | None,
    ) -> None:
        await self.fsm.state(WaitingEmojiToBuyState)

        if emoji_str is None:
            await self.player_views.render_invalid_emoji_to_buy_view(location)
            return

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await self.player_views.render_invalid_emoji_to_buy_view(location)
            return

        purchased_emoji_id, current_datetime = await gather(
            self.uuids.random_uuid(),
            self.clock.current_datetime(),
        )

        async with self.transaction:
            player = await self.players.player_with_id(location.player_id)

            if player is None:
                await self.player_views.render_player_is_not_registered_view(
                    location,
                )
                await self.fsm.set(None)
                return

            tracking = Tracking()
            try:
                player.buy_emoji(
                    emoji, purchased_emoji_id, tracking, current_datetime,
                )
            except EmojiAlreadyPurchasedError:
                await self.fsm.set(None)
                await self.player_views.render_emoji_already_purchased_view(
                    location,
                )
            except NotEnoughStarsError as error:
                await self.fsm.set(None)
                await (
                    self.player_views
                    .render_not_enough_stars_to_buy_emoji_view(
                        location, error.stars_to_become_enough,
                    )
                )
            else:
                await self.map_(tracking)
                await self.fsm.set(None)
                await self.player_views.render_emoji_was_purchased_view(
                    location,
                )
