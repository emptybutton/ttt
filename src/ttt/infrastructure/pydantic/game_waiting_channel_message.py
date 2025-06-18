from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from ttt.application.game.ports.game_waiting_channel import (
    GameWaitingChannelMessage,
    GameWaitingChannelNoGameMessage,
    GameWaitingChannelOkMessage,
    GameWaitingChannelPlayerInGameMessage,
)


class EncodableGameWaitingChannelOkMessage(BaseModel):
    type: Literal["ok"] = "ok"
    player_id: int
    game_id: UUID

    def entity(self) -> GameWaitingChannelOkMessage:
        return GameWaitingChannelOkMessage(
            player_id=self.player_id,
            game_id=self.game_id,
        )

    @classmethod
    def of(
        cls, it: GameWaitingChannelOkMessage,
    ) -> "EncodableGameWaitingChannelOkMessage":
        return EncodableGameWaitingChannelOkMessage(
            player_id=it.player_id,
            game_id=it.game_id,
        )


class EncodableGameWaitingChannelPlayerInGameMessage(BaseModel):
    type: Literal["player_in_game"] = "player_in_game"
    player_id: int

    def entity(self) -> GameWaitingChannelPlayerInGameMessage:
        return GameWaitingChannelPlayerInGameMessage(
            player_id=self.player_id,
        )

    @classmethod
    def of(
        cls, it: GameWaitingChannelPlayerInGameMessage,
    ) -> "EncodableGameWaitingChannelPlayerInGameMessage":
        return EncodableGameWaitingChannelPlayerInGameMessage(
            player_id=it.player_id,
        )


class EncodableGameWaitingChannelNoGameMessage(BaseModel):
    type: Literal["no_game"] = "no_game"
    player_id: int

    def entity(self) -> GameWaitingChannelNoGameMessage:
        return GameWaitingChannelNoGameMessage(
            player_id=self.player_id,
        )

    @classmethod
    def of(
        cls, it: GameWaitingChannelNoGameMessage,
    ) -> "EncodableGameWaitingChannelNoGameMessage":
        return EncodableGameWaitingChannelNoGameMessage(
            player_id=it.player_id,
        )


EncodableGameWaitingChannelMessage = (
    EncodableGameWaitingChannelOkMessage
    | EncodableGameWaitingChannelPlayerInGameMessage
    | EncodableGameWaitingChannelNoGameMessage
)


def encodable_game_waiting_channel_message(
    it: GameWaitingChannelMessage,
) -> EncodableGameWaitingChannelMessage:
    match it:
        case GameWaitingChannelOkMessage():
            return EncodableGameWaitingChannelOkMessage.of(it)

        case GameWaitingChannelPlayerInGameMessage():
            return EncodableGameWaitingChannelPlayerInGameMessage.of(it)

        case GameWaitingChannelNoGameMessage():
            return EncodableGameWaitingChannelNoGameMessage.of(it)
