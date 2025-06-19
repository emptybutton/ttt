from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GameStartedMessage:
    player_id: int
    game_id: UUID


@dataclass(frozen=True)
class PlayerInGameMessage:
    player_id: int


@dataclass(frozen=True)
class NoGameMessage:
    player_id: int


type GameMessage = GameStartedMessage | PlayerInGameMessage | NoGameMessage
