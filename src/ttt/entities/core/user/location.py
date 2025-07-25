from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserGameLocation:
    user_id: int
    game_id: UUID
