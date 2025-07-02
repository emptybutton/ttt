from asyncio import gather
from dataclasses import dataclass

from ttt.application.player.common.ports.player_fsm import (
    PlayerFsm,
    WaitingEmojiToBuyState,
)
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitEmojiToBuy:
    fsm: PlayerFsm
    player_views: PlayerViews

    async def __call__(self, location: PlayerLocation) -> None:
        await gather(
            self.fsm.set(WaitingEmojiToBuyState()),
            self.player_views.render_wait_emoji_to_buy_view(location),
        )
