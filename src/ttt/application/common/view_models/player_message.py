from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerIsNotRegisteredMessage:
    player_id: int


type PlayerMessage = PlayerIsNotRegisteredMessage
