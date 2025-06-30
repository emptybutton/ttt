from ttt.entities.finance.rubles import Rubles


type Stars = int


class NonExchangeableRublesForStarsError(Exception): ...


def purchased_stars_for_rubles(rubles: Rubles) -> Stars:
    """
    :raises ttt.entities.core.stars.NonExchangeableRublesForStarsError:
    """

    match rubles.total_kopecks():
        case 128_00:
            return 8192
        case 256_00:
            return 16384
        case 512_00:
            return 32768
        case 1024_00:
            return 65536
        case _:
            raise NonExchangeableRublesForStarsError
