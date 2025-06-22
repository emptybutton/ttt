from dataclasses import dataclass

from ttt.application.common.dto.player_message import (
    PlayerIsNotRegisteredMessage,
)
from ttt.application.common.ports.player_message_sending import (
    PlayerMessageSending,
)
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.dto.game_message import (
    DoubleWaitingForGameMessage,
    WaitingForGameMessage,
)
from ttt.application.game.ports.game_message_sending import GameMessageSending
from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    players: Players
    waiting_locations: WaitingLocations
    player_message_sending: PlayerMessageSending
    game_message_sending: GameMessageSending
    transaction: Transaction

    async def __call__(self, location: PlayerLocation) -> None:
        async with self.transaction:
            if not await self.players.contains_player_with_id(
                location.player_id,
            ):
                await self.player_message_sending.send_message(
                    PlayerIsNotRegisteredMessage(location),
                )
                return

            push = await self.waiting_locations.push(location)

            if push.was_location_dedublicated:
                await self.game_message_sending.send_message(
                    DoubleWaitingForGameMessage(location),
                )
            else:
                await self.game_message_sending.send_message(
                    WaitingForGameMessage(location),
                )
