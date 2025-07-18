from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ttt.entities.core.stars import (
    Stars,
    has_stars_price,
    price_of_stars,
)
from ttt.entities.core.user.location import UserLocation
from ttt.entities.finance.payment.payment import Payment
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class InvalidStarsForStarsPurchaseError(Exception): ...


@dataclass(frozen=True)
class StarsPurchaseAlreadyCompletedError(Exception):
    is_cancelled: bool


@dataclass
class StarsPurchase:
    """
    :raises ttt.entities.user.stars_purchase.InvalidStarsForStarsPurchaseError:
    """

    id_: UUID
    location: UserLocation
    stars: Stars
    payment: Payment | None

    def __post_init__(self) -> None:
        assert_(
            has_stars_price(self.stars),
            else_=InvalidStarsForStarsPurchaseError,
        )

    def start_payment(
        self, payment_id: UUID, current_datetime: datetime, tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.finance.payment.payment.PaymentIsAlreadyBeingMadeError:
        """  # noqa: E501

        payment = Payment.start(
            self.payment,
            payment_id,
            price_of_stars(self.stars),
            current_datetime,
            tracking,
        )
        self.payment = payment
        tracking.register_mutated(self)

    @classmethod
    def start(
        cls,
        purchase_id: UUID,
        purchase_location: UserLocation,
        purchase_stars: Stars,
        tracking: Tracking,
    ) -> "StarsPurchase":
        """
        :raises ttt.entities.core.stars.InvalidStarsForStarsPurchaseError:
        """

        purchase = StarsPurchase(
            id_=purchase_id,
            location=purchase_location,
            stars=purchase_stars,
            payment=None,
        )
        tracking.register_new(purchase)

        return purchase
