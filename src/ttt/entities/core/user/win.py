from dataclasses import dataclass

from ttt.entities.core.stars import Stars


@dataclass(frozen=True)
class UserWin:
    user_id: int
    new_stars: Stars | None
