from dataclasses import dataclass
from uuid import UUID


@dataclass
class GameLocation:
    player_id: int
    chat_id: int
    game_id: UUID

    def just(self) -> "JustLocation":
        return JustLocation(self.player_id, self.chat_id)


@dataclass
class JustLocation:
    player_id: int
    chat_id: int

    def game(self, game_id: UUID) -> GameLocation:
        return GameLocation(self.player_id, self.chat_id, game_id)


type Location = GameLocation | JustLocation
