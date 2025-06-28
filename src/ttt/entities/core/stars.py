from ttt.entities.finance.kopecks import Kopecks


type Stars = int


class NonExchangeableKopecksForStarsError(Exception): ...


def purchased_stars_for_kopecks(kopecks: Kopecks) -> Stars:
    """
    :raises ttt.entities.core.stars.NonExchangeableKopecksForStarsError:
    """

    match kopecks:
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
            raise NonExchangeableKopecksForStarsError
