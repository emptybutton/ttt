from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.core.stars import Stars, purchased_stars_for_rubles
from ttt.entities.finance.payment.payment import Payment
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class NoNewStarsForStarsPurchaseError(Exception): ...


@dataclass(frozen=True)
class StarsPurchaseAlreadyCompletedError(Exception):
    is_cancelled: bool


@dataclass
class StarsPurchase:
    """
    :raises ttt.entities.player.stars_purchase.NoNewStarsForStarsPurchaseError:
    """

    id_: UUID
    location: PlayerLocation
    new_stars: Stars
    payment: Payment

    def __post_init__(self) -> None:
        assert_(self.new_stars >= 0, else_=NoNewStarsForStarsPurchaseError)

    @classmethod
    def initiate_payment(  # noqa: PLR0913, PLR0917
        cls,
        purchase_id: UUID,
        purchase_location: PlayerLocation,
        payment_id: UUID,
        paid_rubles: Rubles,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> "StarsPurchase":
        """
        :raises ttt.entities.core.stars.NonExchangeableRublesForStarsError:
        """

        payment = Payment.initiate(
            payment_id, paid_rubles, current_datetime, tracking,
        )

        purchase = StarsPurchase(
            id_=purchase_id,
            location=purchase_location,
            new_stars=purchased_stars_for_rubles(paid_rubles),
            payment=payment,
        )
        tracking.register_new(purchase)

        return purchase
