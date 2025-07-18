from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from ttt.entities.core.game.win import AiWin
from ttt.entities.tools.tracking import Tracking


class AiType(Enum):
    gemini_2_0_flash = auto()


@dataclass(frozen=True)
class Ai:
    id: UUID
    type: AiType

    def win(self) -> AiWin:
        return AiWin(self.id)


def create_ai(ai_id: UUID, ai_type: AiType, tracking: Tracking) -> Ai:
    ai = Ai(ai_id, ai_type)
    tracking.register_new(ai)

    return ai
