from ttt.entities.finance.rubles import Rubles


type Stars = int


class NonExchangeableRublesForStarsError(Exception): ...


def purchased_stars_for_rubles(rubles: Rubles) -> Stars:
    """
    :raises ttt.entities.core.stars.NonExchangeableRublesForStarsError:
    """

    match rubles.total_kopecks():
        case 8_00:
            return 256
        case 64_00:
            return 2048
        case 128_00:
            return 4096
        case 256_00:
            return 10240
        case 512_00:
            return 32768
        case 1024_00:
            return 131072
        case _:
            raise NonExchangeableRublesForStarsError
