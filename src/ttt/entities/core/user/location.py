from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserLocation:
    user_id: int
    chat_id: int

    def game(self, game_id: UUID) -> "UserGameLocation":
        return UserGameLocation(self.user_id, self.chat_id, game_id)


@dataclass
class UserGameLocation:
    user_id: int
    chat_id: int
    game_id: UUID
