def short_float_text(float_: float) -> str:
    return str(int(float_)) if float_ == int(float_) else f"{float_:.2f}"


def copy_signed_text(text: str, original_signed: float) -> str:
    return f"+{text}" if original_signed >= 0 else f"{text}"


def signed_number_text(number: float) -> str:
    return f"+{number}" if number >= 0 else f"{number}"
