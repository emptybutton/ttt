from typing import Literal

from ttt.entities.elo.rating import EloRating


type RankTier = Literal[-1, 0, 1, 2, 3, 4]
type Rank = RankTier


def rank(rating: EloRating) -> Rank:
    if rating <= 871:
        return -1
    if 872 <= rating <= 1085:
        return 0
    if 1086 <= rating <= 1337:
        return 1
    if 1337 <= rating <= 1679:
        return 2
    if 1680 <= rating <= 1999:
        return 3

    return 4


def are_ranks_adjacent(rank1: Rank, rank2: Rank) -> bool:
    return rank1 - 1 == rank2 or rank1 + 1 == rank2
