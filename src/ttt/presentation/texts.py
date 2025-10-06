from ttt.entities.core.user.rank import IntervalRank, Rank, rank_with_tier
from ttt.entities.elo.rating import EloRating


def short_float_text(float_: float) -> str:
    return str(int(float_)) if float_ == int(float_) else f"{float_:.2f}"


def copy_signed_text(text: str, original_signed: float) -> str:
    return f"+{text}" if original_signed >= 0 else f"{text}"


def rank_sign(rank_: Rank) -> str:  # noqa: PLR0911
    match rank_.tier:
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
        case 5:
            return "⚪️"


def rank_name(rank_: Rank) -> str:  # noqa: PLR0911
    match rank_.tier:
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
        case 5:
            return "Сильнейший"


def rank_title(rank_: Rank) -> str:
    return f"{rank_sign(rank_)} {rank_name(rank_)}"


def rank_progres_text(rank_: Rank, raiting: EloRating) -> str:
    if rank_.tier == 4 or rank_.tier == 5:  # noqa: PLR1714, PLR2004
        return f"({short_float_text(raiting)})"

    next_rank = rank_with_tier(rank_.tier + 1)  # type: ignore[arg-type]
    if not isinstance(next_rank, IntervalRank):
        raise TypeError

    return f"({short_float_text(raiting)} / {next_rank.min_rating})"
