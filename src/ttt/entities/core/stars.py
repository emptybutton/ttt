from ttt.entities.finance.kopecks import Kopecks
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.assertion import not_none


type Stars = int


class NonExchangeableRublesForStarsError(Exception): ...


_price_stars_map: dict[Kopecks, Stars] = {
    128_00: 8192,
    256_00: 16384,
    512_00: 32768,
    1024_00: 65536,
}
_stars_price_map: dict[Stars, Kopecks] = dict(
    zip(
        _price_stars_map.values(),
        _price_stars_map.keys(),
        strict=True,
    ),
)


def stars_of_price(rubles: Rubles) -> Stars:
    """
    :raises ttt.entities.core.stars.NonExchangeableRublesForStarsError:
    """

    stars = _price_stars_map.get(rubles.total_kopecks())

    return not_none(stars, else_=NonExchangeableRublesForStarsError)


def price_of_stars(stars: Stars) -> Rubles:
    """
    :raises ttt.entities.core.stars.NonExchangeableRublesForStarsError:
    """

    total_kopecks = _stars_price_map.get(stars)
    total_kopecks = not_none(
        total_kopecks,
        else_=NonExchangeableRublesForStarsError,
    )

    return Rubles.with_total_kopecks(total_kopecks)


def has_stars_price(stars: Stars) -> bool:
    return stars in _stars_price_map
