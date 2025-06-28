from dataclasses import dataclass
from datetime import datetime

from ttt.entities.core.player.kopecks import Kopecks
from ttt.entities.core.player.stars import Stars
from ttt.entities.tools.assertion import assert_


class NoStarsForStarsPurchaseError(Exception): ...


class NoKopecksForStarsPurchaseError(Exception): ...


@dataclass(frozen=True)
class StarsPurchase:
    """
    :raises ttt.entities.player.payment.NoStarsForStarsPurchaseError:
    :raises ttt.entities.player.payment.NoKopecksForStarsPurchaseError:
    """

    id_: str
    payment_gateway_id: str
    player_id: int
    stars: Stars
    kopecks: Kopecks
    datetime_: datetime

    def __post_init__(self) -> None:
        assert_(self.stars >= 0, else_=NoStarsForStarsPurchaseError)
        assert_(self.kopecks >= 0, else_=NoKopecksForStarsPurchaseError)
