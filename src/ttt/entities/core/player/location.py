from dataclasses import dataclass
from uuid import UUID

from ttt.entities.telegram.message import MessageGlobalID


@dataclass
class JustLocation:
    player_id: int
    chat_id: int


@dataclass
class GameLocation:
    player_id: int
    game_id: UUID
    message_id: MessageGlobalID

    def just(self) -> JustLocation:
        return JustLocation(self.player_id, self.message_id.chat_id)


type Location = GameLocation | JustLocation
