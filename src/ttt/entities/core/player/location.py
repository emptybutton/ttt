from dataclasses import dataclass
from uuid import UUID


@dataclass
class PlayerLocation:
    player_id: int
    chat_id: int

    def game(self, game_id: UUID) -> "PlayerGameLocation":
        return PlayerGameLocation(self.player_id, self.chat_id, game_id)


@dataclass
class PlayerGameLocation:
    player_id: int
    chat_id: int
    game_id: UUID
