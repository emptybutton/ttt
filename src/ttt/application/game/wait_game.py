from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.player_message_views import PlayerMessageViews
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.view_models.player_message import (
    PlayerIsNotRegisteredMessage,
)
from ttt.application.game.ports.game_channel import (
    GameChannel,
    GameChannelTimeoutError,
)
from ttt.application.game.ports.game_message_views import GameMessageViews
from ttt.application.game.ports.waiting_player_id_pairs import (
    WaitingPlayerIdPairs,
)
from ttt.application.game.view_models.game_message import NoGameMessage


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    players: Players
    waiting_player_id_pairs: WaitingPlayerIdPairs
    game_channel: GameChannel
    game_message_views: GameMessageViews
    player_message_views: PlayerMessageViews
    transaction: Transaction

    async def __call__(self, player_id: int) -> None:
        async with self.transaction:
            if not await self.players.contains_player_with_id(player_id):
                await self.player_message_views.render_message_for_one_player(
                    PlayerIsNotRegisteredMessage(player_id),
                )
                return

            message, _, = await gather(
                self.game_channel.wait(player_id),
                self.waiting_player_id_pairs.push(player_id),
            )
            if isinstance(message, GameChannelTimeoutError):
                message = NoGameMessage(player_id)

            await self.game_message_views.render_message_for_one_player(
                message,
            )
