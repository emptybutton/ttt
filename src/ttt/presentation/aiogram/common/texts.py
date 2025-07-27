def short_float_text(float_: float) -> str:
    return str(int(float_)) if float_ == int(float_) else f"{float_:.2f}"
