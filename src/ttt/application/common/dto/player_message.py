from dataclasses import dataclass

from ttt.entities.core.player.location import PlayerLocation


@dataclass(frozen=True)
class PlayerIsNotRegisteredMessage:
    location: PlayerLocation


@dataclass(frozen=True)
class PlayerAlreadyRegisteredMessage:
    location: PlayerLocation


@dataclass(frozen=True)
class PlayerRegisteredMessage:
    location: PlayerLocation


type PlayerMessage = (
    PlayerIsNotRegisteredMessage
    | PlayerAlreadyRegisteredMessage
    | PlayerRegisteredMessage
)
