from dataclasses import dataclass

from ttt.entities.core.stars import Stars


@dataclass(frozen=True)
class Win:
    winner_id: int
    new_stars: Stars
