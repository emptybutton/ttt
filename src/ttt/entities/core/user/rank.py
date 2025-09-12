import math
from dataclasses import dataclass
from typing import Literal

from ttt.entities.elo.rating import EloRating


type RankTier = Literal[-1, 0, 1, 2, 3, 4]


@dataclass(frozen=True)
class Rank:
    tier: RankTier
    min_rating: EloRating
    max_rating: EloRating


ranks = (
    Rank(tier=-1, min_rating=-math.inf, max_rating=871),
    Rank(tier=0, min_rating=872, max_rating=1085),
    Rank(tier=1, min_rating=1086, max_rating=1336),
    Rank(tier=2, min_rating=1337, max_rating=1679),
    Rank(tier=3, min_rating=1680, max_rating=1999),
    Rank(tier=4, min_rating=2000, max_rating=math.inf),
)


def rank_with_tier(tier: RankTier) -> Rank:
    for rank in ranks:
        if rank.tier == tier:
            return rank

    raise ValueError


def rank_for_rating(rating: EloRating) -> Rank:
    for rank in ranks:
        if rank.min_rating <= rating <= rank.max_rating:
            return rank

    raise ValueError


def are_ranks_adjacent(rank1: Rank, rank2: Rank) -> bool:
    return rank1.tier + 1 == rank2.tier or rank1.tier - 1 == rank2.tier
