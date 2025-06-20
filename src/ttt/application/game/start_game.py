from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.dto.game_message import (
    GameStartedMessage,
    NoGameMessage,
    PlayerAlreadyInGameMessage,
)
from ttt.application.game.ports.game_message_sending import GameMessageSending
from ttt.application.game.ports.games import Games
from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.entities.core.game.game import (
    PlayersAlreadyInGameError,
    start_game,
)
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGame:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    players: Players
    games: Games
    game_message_sending: GameMessageSending
    waiting_locations: WaitingLocations
    transaction: Transaction

    async def __call__(self) -> None:
        async for player1_location, player2_location in self.waiting_locations:
            async with self.transaction:
                player1, player2 = await self.players.players_with_ids(
                    (player1_location.player_id, player2_location.player_id),
                )
                game_id, cell_id_matrix, player1_emoji, player2_emoji = (
                    await gather(
                        self.uuids.random_uuid(),
                        self.uuids.random_uuid_matrix((3, 3)),
                        self.emojis.random_emoji(),
                        self.emojis.random_emoji(),
                    )
                )

                player1_location_message_id, player2_location_message_id = (
                    await self.game_message_sending.send_messages((
                        GameStartedMessage(not_none(player1.game_location)),
                        GameStartedMessage(not_none(player1.game_location)),
                    ))
                )

                tracking = Tracking()
                try:
                    start_game(
                        cell_id_matrix,
                        game_id,
                        player1,
                        player1_emoji,
                        player1_location_message_id,
                        player2,
                        player2_emoji,
                        player2_location_message_id,
                        tracking,
                    )
                except PlayersAlreadyInGameError as error:
                    players_and_locations = (
                        (player1, player1_location),
                        (player2, player2_location),
                    )
                    await self.game_message_sending.send_messages(tuple(
                        PlayerAlreadyInGameMessage(location)
                        if player in error.players
                        else NoGameMessage(location)
                        for player, location in players_and_locations
                    ))
                    continue
                else:
                    await self.map_(tracking)
