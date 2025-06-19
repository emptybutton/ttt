from typing import Literal

from pydantic import BaseModel

from ttt.application.game.dto.game_message import (
    GameStartedMessage,
    GameStartMessage,
    NoGameMessage,
    PlayerAlreadyInGameMessage,
)
from ttt.entities.core.player.location import GameLocation, JustLocation


class EncodableGameStartedMessage(BaseModel):
    type: Literal["ok"] = "ok"
    location: GameLocation

    def entity(self) -> GameStartedMessage:
        return GameStartedMessage(location=self.location)

    @classmethod
    def of(
        cls,
        it: GameStartedMessage,
    ) -> "EncodableGameStartedMessage":
        return EncodableGameStartedMessage(location=it.location)


class EncodablePlayerInGameMessage(BaseModel):
    type: Literal["player_in_game"] = "player_in_game"
    location: JustLocation

    def entity(self) -> PlayerAlreadyInGameMessage:
        return PlayerAlreadyInGameMessage(location=self.location)

    @classmethod
    def of(
        cls,
        it: PlayerAlreadyInGameMessage,
    ) -> "EncodablePlayerInGameMessage":
        return EncodablePlayerInGameMessage(location=it.location)


class EncodableNoGameMessage(BaseModel):
    type: Literal["no_game"] = "no_game"
    location: JustLocation

    def entity(self) -> NoGameMessage:
        return NoGameMessage(location=self.location)

    @classmethod
    def of(
        cls,
        it: NoGameMessage,
    ) -> "EncodableNoGameMessage":
        return EncodableNoGameMessage(location=it.location)


EncodableGameStartMessage = (
    EncodableGameStartedMessage
    | EncodablePlayerInGameMessage
    | EncodableNoGameMessage
)


def encodable_game_start_message(
    it: GameStartMessage,
) -> EncodableGameStartMessage:
    match it:
        case GameStartedMessage():
            return EncodableGameStartedMessage.of(it)

        case PlayerAlreadyInGameMessage():
            return EncodablePlayerInGameMessage.of(it)

        case NoGameMessage():
            return EncodableNoGameMessage.of(it)
