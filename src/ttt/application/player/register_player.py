from dataclasses import dataclass

from ttt.application.common.dto.player_message import (
    PlayerAlreadyRegisteredMessage,
    PlayerRegisteredMessage,
)
from ttt.application.common.ports.map import Map, NotUniquePlayerIdError
from ttt.application.common.ports.player_message_sending import (
    PlayerMessageSending,
)
from ttt.application.common.ports.transaction import Transaction
from ttt.entities.core.player.location import JustLocation
from ttt.entities.core.player.player import register_player
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class RegisterPlayer:
    transaction: Transaction
    player_message_sending: PlayerMessageSending
    map: Map

    async def __call__(self, player_id: int, player_chat_id: int) -> None:
        location = JustLocation(player_id, player_chat_id)

        tracking = Tracking()
        register_player(player_id, tracking)

        async with self.transaction:
            try:
                await self.map(tracking)
            except NotUniquePlayerIdError:
                await self.player_message_sending.send_message(
                    PlayerAlreadyRegisteredMessage(location),
                )
            else:
                await self.player_message_sending.send_message(
                    PlayerRegisteredMessage(location),
                )
