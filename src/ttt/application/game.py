from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common import (
    Games,
    GameViews,
    GameWaitingChannel,
    GameWaitingChannelNoGameMessage,
    GameWaitingChannelOkMessage,
    GameWaitingChannelPlayerInGameMessage,
    Map,
    Players,
    Transaction,
    UUIDs,
    WaitingPlayerIdPairs,
)
from ttt.entities.core import (
    GameResult,
    PlayerAlreadyInGameError,
    start_game,
)
from ttt.entities.math import Vector
from ttt.entities.tools import Tracking, not_none


@dataclass(frozen=True, unsafe_hash=False)
class WaitGameOutput:
    game_id: UUID


class GameTimeoutError(Exception): ...


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    players: Players
    waiting_player_id_pairs: WaitingPlayerIdPairs
    game_channel: GameWaitingChannel
    transaction: Transaction

    async def __call__(self, player_id: int) -> WaitGameOutput:
        """
        :raises ttt.application.common.NoPlayerError:
        :raises ttt.application.game.GameTimeoutError:
        :raises ttt.application.common.GameWaitingChannelPlayerInGameMessage:
        :raises ttt.application.common.GameWaitingChannelNoGameMessage:
        :raises ttt.application.common.GameWaitingChannelTimeoutError:
        """

        await self.players.assert_contains_player_with_id(player_id)

        message, _, = await gather(
            self.game_channel.wait(player_id),
            self.waiting_player_id_pairs.push(player_id),
        )
        message = not_none(message, else_=GameTimeoutError)

        match message:
            case GameWaitingChannelOkMessage():
                return WaitGameOutput(message.game_id)
            case Exception():
                raise message


@dataclass(frozen=True, unsafe_hash=False)
class StartGame:
    map_: Map
    uuids: UUIDs
    players: Players
    games: Games
    waiting_player_id_pairs: WaitingPlayerIdPairs
    game_channel: GameWaitingChannel
    transaction: Transaction

    async def __call__(self) -> None:
        async for player1_id, player2_id in self.waiting_player_id_pairs:
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
                    GameWaitingChannelPlayerInGameMessage(player.id)
                    if player in error.players
                    else GameWaitingChannelNoGameMessage(player.id)
                    for player in (player1, player2)
                ))
            else:
                async with self.transaction:
                    await gather(
                        self.map_(tracking),
                        self.game_channel.publish_many((
                            GameWaitingChannelOkMessage(player1.id, game.id),
                            GameWaitingChannelOkMessage(player1.id, game.id),
                        )),
                    )


@dataclass(frozen=True, unsafe_hash=False)
class MakeMoveInGame:
    map_: Map
    games: Games
    players: Players
    transaction: Transaction

    async def __call__(
        self, player_id: int, cell_position: Vector,
    ) -> GameResult | None:
        """
        :raises ttt.application.common.NoPlayerError:
        :raises ttt.application.common.NoGameError:
        :raises ttt.entities.core.CompletedGameError:
        :raises ttt.entities.core.NotCurrentPlayerError:
        :raises ttt.entities.core.NoCellError:
        :raises ttt.entities.core.AlreadyFilledCellError:
        """

        player = await self.players.player_with_id(player_id)
        game = await self.games.game_with_id(player.current_game_id)

        game_result = game.make_move(player.id, cell_position)

        async with self.transaction:
            await self.map_(game.tracking)

        return game_result


@dataclass(frozen=True, unsafe_hash=False)
class ViewGame[GameViewT]:
    game_views: GameViews[GameViewT]
    transaction: Transaction

    async def __call__(self, player_id: int) -> GameViewT:
        async with self.transaction:
            return await self.game_views.view_game_of_player_with_id(player_id)
