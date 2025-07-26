from ttt.entities.elo.score import ExpectedScore, WinningScore


type EloRating = float


initial_elo_rating: EloRating = 1000


def new_elo_rating(
    rating: EloRating,
    other_rating: EloRating,
    winning_score: WinningScore,
    games_played: int,
) -> EloRating:
    expected_score = _expected_score(rating, other_rating)

    if _is_player_newbie(games_played):
        k = 40
    elif float(rating) >= 2400:  # noqa: PLR2004
        k = 10
    else:
        k = 20

    return rating + k * (winning_score.value - expected_score)


def _is_player_newbie(games_played: int) -> bool:
    return games_played <= 30  # noqa: PLR2004


def _expected_score(rating_a: EloRating, rating_b: EloRating) -> ExpectedScore:
    return 1 / (1 + 10 ** ((float(rating_b) - float(rating_a)) / 400))
