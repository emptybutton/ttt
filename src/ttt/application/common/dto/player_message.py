from dataclasses import dataclass

from ttt.entities.core.player.location import JustLocation


@dataclass(frozen=True)
class PlayerIsNotRegisteredMessage:
    location: JustLocation


@dataclass(frozen=True)
class PlayerAlreadyRegisteredMessage:
    location: JustLocation


@dataclass(frozen=True)
class PlayerRegisteredMessage:
    location: JustLocation


type PlayerMessage = (
    PlayerIsNotRegisteredMessage
    | PlayerAlreadyRegisteredMessage
    | PlayerRegisteredMessage
)
