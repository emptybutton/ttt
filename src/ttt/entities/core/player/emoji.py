from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ttt.entities.text.emoji import Emoji


@dataclass(frozen=True)
class PlayerEmoji:
    id: UUID
    player_id: int
    emoji: Emoji
    datetime_of_purchase: datetime
