from asyncio import gather
from dataclasses import dataclass
from uuid import UUID

from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.game.ports.game_waiting_channel import (
    GameWaitingChannel,
    GameWaitingChannelNoGameMessage,
    GameWaitingChannelOkMessage,
    GameWaitingChannelPlayerInGameMessage,
    GameWaitingChannelTimeoutError,
)
from ttt.application.game.ports.waiting_player_id_pairs import (
    WaitingPlayerIdPairs,
)
from ttt.entities.tools.assertion import not_none


@dataclass(frozen=True, unsafe_hash=False)
class Output:
    game_id: UUID


class GameTimeoutError(Exception): ...


@dataclass(frozen=True, unsafe_hash=False)
class WaitGame:
    players: Players
    waiting_player_id_pairs: WaitingPlayerIdPairs
    game_channel: GameWaitingChannel
    transaction: Transaction

    async def __call__(self, player_id: int) -> Output:  # type: ignore[return]
        """
        :raises ttt.application.common.ports.players.NoPlayerError:
        :raises ttt.application.wait_game.GameTimeoutError:
        :raises ttt.application.game.ports.game_waiting_channel.GameWaitingChannelPlayerInGameMessage:
        :raises ttt.application.game.ports.game_waiting_channel.GameWaitingChannelNoGameMessage:
        :raises ttt.application.game.ports.game_waiting_channel.GameWaitingChannelTimeoutError:
        """  # noqa: E501

        await self.players.assert_contains_player_with_id(player_id)

        message, _, = await gather(
            self.game_channel.wait(player_id),
            self.waiting_player_id_pairs.push(player_id),
        )
        message = not_none(message, else_=GameTimeoutError)

        match message:
            case GameWaitingChannelOkMessage():
                return Output(message.game_id)
            case GameWaitingChannelPlayerInGameMessage():
                raise message
            case GameWaitingChannelNoGameMessage():
                raise message
            case GameWaitingChannelTimeoutError():
                raise message
