from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.ports.game_channel import GameChannel
from ttt.application.game.ports.games import Games
from ttt.application.game.ports.waiting_player_id_pairs import (
    WaitingPlayerIdPairs,
)
from ttt.application.game.view_models.game_message import (
    GameStartedMessage,
    NoGameMessage,
    PlayerInGameMessage,
)
from ttt.entities.core.game.game import PlayerAlreadyInGameError, start_game
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGame:
    map_: Map
    uuids: UUIDs
    players: Players
    games: Games
    waiting_player_id_pairs: WaitingPlayerIdPairs
    game_channel: GameChannel
    transaction: Transaction

    async def __call__(self) -> None:
        async for player1_id, player2_id in self.waiting_player_id_pairs:
            async with self.transaction:
                player1, player2 = await self.players.players_with_id(
                    player1_id, player2_id,
                )
                game_id, cell_id_matrix = await gather(
                    self.uuids.random_uuid(),
                    self.uuids.random_uuid_matrix((3, 3)),
                )

                tracking = Tracking()
                try:
                    game = start_game(
                        cell_id_matrix, game_id, player1, player2, tracking,
                    )
                except PlayerAlreadyInGameError as error:
                    await self.game_channel.publish_many(tuple(
                        PlayerInGameMessage(player.id)
                        if player in error.players
                        else NoGameMessage(player.id)
                        for player in (player1, player2)
                    ))
                else:
                    await gather(
                        self.map_(tracking),
                        self.game_channel.publish_many((
                            GameStartedMessage(player1.id, game.id),
                            GameStartedMessage(player1.id, game.id),
                        )),
                    )
