from ttt.entities.core.user.rank import Rank


def short_float_text(float_: float) -> str:
    return str(int(float_)) if float_ == int(float_) else f"{float_:.2f}"


def copy_signed_text(text: str, original_signed: float) -> str:
    return f"+{text}" if original_signed >= 0 else f"{text}"


def rank_text(rank: Rank) -> str:
    match rank:
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
