from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.user.win import UserWin


@dataclass(frozen=True)
class AiWin:
    ai_id: UUID


type Win = UserWin | AiWin
