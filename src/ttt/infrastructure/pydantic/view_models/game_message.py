from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from ttt.application.game.view_models.game_message import (
    GameMessage,
    GameStartedMessage,
    NoGameMessage,
    PlayerInGameMessage,
)


class EncodableGameStartedMessage(BaseModel):
    type: Literal["ok"] = "ok"
    player_id: int
    game_id: UUID

    def entity(self) -> GameStartedMessage:
        return GameStartedMessage(
            player_id=self.player_id,
            game_id=self.game_id,
        )

    @classmethod
    def of(
        cls, it: GameStartedMessage,
    ) -> "EncodableGameStartedMessage":
        return EncodableGameStartedMessage(
            player_id=it.player_id,
            game_id=it.game_id,
        )


class EncodablePlayerInGameMessage(BaseModel):
    type: Literal["player_in_game"] = "player_in_game"
    player_id: int

    def entity(self) -> PlayerInGameMessage:
        return PlayerInGameMessage(
            player_id=self.player_id,
        )

    @classmethod
    def of(
        cls, it: PlayerInGameMessage,
    ) -> "EncodablePlayerInGameMessage":
        return EncodablePlayerInGameMessage(
            player_id=it.player_id,
        )


class EncodableNoGameMessage(BaseModel):
    type: Literal["no_game"] = "no_game"
    player_id: int

    def entity(self) -> NoGameMessage:
        return NoGameMessage(
            player_id=self.player_id,
        )

    @classmethod
    def of(
        cls, it: NoGameMessage,
    ) -> "EncodableNoGameMessage":
        return EncodableNoGameMessage(
            player_id=it.player_id,
        )


EncodableGameMessage = (
    EncodableGameStartedMessage
    | EncodablePlayerInGameMessage
    | EncodableNoGameMessage
)


def encodable_game_message(
    it: GameMessage,
) -> EncodableGameMessage:
    match it:
        case GameStartedMessage():
            return EncodableGameStartedMessage.of(it)

        case PlayerInGameMessage():
            return EncodablePlayerInGameMessage.of(it)

        case NoGameMessage():
            return EncodableNoGameMessage.of(it)
