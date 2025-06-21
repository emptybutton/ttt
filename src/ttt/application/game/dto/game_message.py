from dataclasses import dataclass

from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True)
class PlayerAlreadyInGameMessage:
    location: PlayerLocation


@dataclass(frozen=True)
class WaitingForGameMessage:
    location: PlayerLocation


type GameMessage = PlayerAlreadyInGameMessage | WaitingForGameMessage
