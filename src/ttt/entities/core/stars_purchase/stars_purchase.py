from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ttt.entities.core.stars import (
    Stars,
    has_stars_price,
    price_of_stars,
)
from ttt.entities.core.user.user import User
from ttt.entities.finance.payment.payment import (
    Payment,
    cancel_payment,
    complete_payment,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class InvalidStarsForStarsPurchaseError(Exception): ...


@dataclass
class StarsPurchaseAlreadyCompletedError(Exception):
    is_cancelled: bool


@dataclass
class StarsPurchase:
    """
    :raises ttt.entities.user.stars_purchase.InvalidStarsForStarsPurchaseError:
    """

    id_: UUID
    user: User
    stars: Stars
    payment: Payment | None

    def __post_init__(self) -> None:
        assert_(
            has_stars_price(self.stars),
            else_=InvalidStarsForStarsPurchaseError,
        )

    @classmethod
    def start(
        cls,
        purchase_id: UUID,
        purchase_user: User,
        purchase_stars: Stars,
        tracking: Tracking,
    ) -> "StarsPurchase":
        """
        :raises ttt.entities.core.stars.InvalidStarsForStarsPurchaseError:
        """

        purchase = StarsPurchase(
            id_=purchase_id,
            user=purchase_user,
            stars=purchase_stars,
            payment=None,
        )
        tracking.register_new(purchase)

        return purchase

    def start_payment(
        self,
        payment_id: UUID,
        current_datetime: datetime,
        tracking: Tracking,
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

    def complete_payment(
        self,
        payment_success: PaymentSuccess,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.finance.payment.payment.NoPaymentError:
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
        """

        self.user.account = self.user.account.map(
            lambda stars: stars + self.stars,
        )
        tracking.register_mutated(self.user)

        complete_payment(
            self.payment,
            payment_success,
            current_datetime,
            tracking,
        )

    def cancel(
        self,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.finance.payment.payment.NoPaymentError:
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
        """

        cancel_payment(self.payment, current_datetime, tracking)


StarsPurchaseAtomic = StarsPurchase
