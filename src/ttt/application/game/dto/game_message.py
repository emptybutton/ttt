from dataclasses import dataclass

from ttt.entities.core.player.location import (
    GameLocation,
    JustLocation,
)


@dataclass(frozen=True)
class GameStartedMessage:
    location: GameLocation


@dataclass(frozen=True)
class PlayerAlreadyInGameMessage:
    location: JustLocation


@dataclass(frozen=True)
class NoGameMessage:
    location: JustLocation


type GameStartMessage = (
    GameStartedMessage | PlayerAlreadyInGameMessage | NoGameMessage
)


@dataclass(frozen=True)
class WaitingForGameMessage:
    location: JustLocation


type GameMessage = GameStartMessage | WaitingForGameMessage
