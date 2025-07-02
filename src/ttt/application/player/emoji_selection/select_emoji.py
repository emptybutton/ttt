from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.player.common.ports.player_fsm import (
    PlayerFsm,
    WaitingEmojiToSelectState,
)
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.application.player.common.ports.players import Players
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.player.player import EmojiNotPurchasedError
from ttt.entities.text.emoji import Emoji, InvalidEmojiError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class SelectEmoji:
    fsm: PlayerFsm
    transaction: Transaction
    players: Players
    player_views: PlayerViews
    map_: Map

    async def __call__(
        self, location: PlayerLocation, emoji_str: str | None,
    ) -> None:
        await self.fsm.state(WaitingEmojiToSelectState)

        if emoji_str is None:
            await self.player_views.render_invalid_emoji_to_select_view(
                location,
            )
            return

        try:
            emoji = Emoji(emoji_str)
        except InvalidEmojiError:
            await self.player_views.render_invalid_emoji_to_select_view(
                location,
            )
            return

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
                player.select_emoji(emoji, tracking)
            except EmojiNotPurchasedError:
                await self.fsm.set(None)
                await (
                    self.player_views
                    .render_emoji_not_purchased_to_select_view(location)
                )
            else:
                await self.map_(tracking)
                await self.fsm.set(None)
                await self.player_views.render_emoji_selected_view(location)
