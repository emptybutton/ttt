from dataclasses import dataclass

from ttt.entities.elo.rating import EloRating


@dataclass(frozen=True)
class UserDraw:
    user_id: int
    rating_vector: EloRating | None
