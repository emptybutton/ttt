from dataclasses import dataclass

from ttt.entities.core.stars import Stars
from ttt.entities.elo.rating import EloRating


@dataclass(frozen=True)
class UserWin:
    user_id: int
    new_stars: Stars | None
    rating_vector: EloRating | None
