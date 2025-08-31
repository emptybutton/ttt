from ttt.entities.core.user.rank import Rank, rank_for_rating, rank_with_tier
from ttt.entities.elo.rating import EloRating


def short_float_text(float_: float) -> str:
    return str(int(float_)) if float_ == int(float_) else f"{float_:.2f}"


def copy_signed_text(text: str, original_signed: float) -> str:
    return f"+{text}" if original_signed >= 0 else f"{text}"


def rank_sign(rank: Rank) -> str:
    match rank.tier:
        case -1:
            return "🪨"
        case 0:
            return "🌱"
        case 1:
            return "🗡"
        case 2:
            return "👾"
        case 3:
            return "👹"
        case 4:
            return "🪬"


def rank_name(rank: Rank) -> str:
    match rank.tier:
        case -1:
            return "Камень"
        case 0:
            return "Росток"
        case 1:
            return "Клинок"
        case 2:
            return "Монстр"
        case 3:
            return "Демон"
        case 4:
            return "Око"


def rank_title(rank: Rank) -> str:
    return f"{rank_sign(rank)} {rank_name(rank)}"


def rank_progres_text(raiting: EloRating) -> str:
    rank = rank_for_rating(raiting)

    if rank.tier == 4:  # noqa: PLR2004
        return f"({short_float_text(raiting)})"

    next_rank = rank_with_tier(rank.tier + 1)  # type: ignore[arg-type]

    return f"({short_float_text(raiting)} / {next_rank.min_rating})"
