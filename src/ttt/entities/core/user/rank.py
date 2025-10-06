import math
from dataclasses import dataclass
from typing import Literal

from ttt.entities.elo.rating import EloRating


type RankTier = Literal[-1, 0, 1, 2, 3, 4, 5]


@dataclass(frozen=True)
class IntervalRank:
    tier: RankTier
    min_rating: EloRating
    max_rating: EloRating


@dataclass(frozen=True)
class SpecialRank[TierT: RankTier, NameT: str]:
    tier: TierT
    name: NameT


StrongestRank = SpecialRank[Literal[5], Literal["strongest"]]
strongest_rank = StrongestRank(tier=5, name="strongest")

special_ranks = (
    strongest_rank,
)


type Rank = IntervalRank | StrongestRank


interval_ranks = (
    IntervalRank(tier=-1, min_rating=-math.inf, max_rating=871),
    IntervalRank(tier=0, min_rating=872, max_rating=1085),
    IntervalRank(tier=1, min_rating=1086, max_rating=1336),
    IntervalRank(tier=2, min_rating=1337, max_rating=1679),
    IntervalRank(tier=3, min_rating=1680, max_rating=1999),
    IntervalRank(tier=4, min_rating=2000, max_rating=math.inf),
)


ranks = (
    *interval_ranks,
    *special_ranks,
)


def rank_with_tier(tier: RankTier) -> Rank:
    for rank in ranks:
        if rank.tier == tier:
            return rank

    raise ValueError


type UsersWithMaxRating = Literal["1", ">1"]


def rank(
    rating: EloRating,
    max_rating: EloRating,
    users_with_max_rating: UsersWithMaxRating,
) -> Rank:
    if rating == max_rating and users_with_max_rating == "1":
        return strongest_rank

    for rank in interval_ranks:
        if rank.min_rating <= rating <= rank.max_rating:
            return rank

    raise ValueError


def are_ranks_adjacent(rank1: Rank, rank2: Rank) -> bool:
    return rank1.tier + 1 == rank2.tier or rank1.tier - 1 == rank2.tier
