from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class NoPaidRublesForPaymentError(Exception): ...


@dataclass(frozen=True)
class PaymentAlreadyCompletedError(Exception):
    is_cancelled: bool


@dataclass
class Payment:
    """
    :raises ttt.entities.finance.payment.payment.NoNewStarsForPaymentError:
    :raises ttt.entities.finance.payment.payment.NoPaidRublesForPaymentError:
    """

    id_: UUID
    paid_rubles: Rubles
    start_datetime: datetime
    completion_datetime: datetime | None
    success: PaymentSuccess | None
    is_cancelled: bool

    def __post_init__(self) -> None:
        assert_(self.paid_rubles, else_=NoPaidRublesForPaymentError)

    def is_completed(self) -> bool:
        return self.success is not None or self.is_cancelled

    def complete(
        self,
        success: PaymentSuccess,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.finance.payment.payment.PaymentAlreadyCompletedError:
        """  # noqa: E501

        assert_(
            not self.is_completed(),
            else_=PaymentAlreadyCompletedError(self.is_cancelled),
        )

        self.success = success
        self.completion_datetime = current_datetime
        tracking.register_mutated(self)

    def cancel(self, current_datetime: datetime, tracking: Tracking) -> None:
        """
        :raises ttt.entities.finance.payment.payment.PaymentAlreadyCompletedError:
        """  # noqa: E501

        assert_(
            not self.is_completed(),
            else_=PaymentAlreadyCompletedError(self.is_cancelled),
        )

        self.is_cancelled = True
        self.completion_datetime = current_datetime
        tracking.register_mutated(self)

    @classmethod
    def initiate(
        cls,
        payment_id: UUID,
        payment_paid_rubles: Rubles,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> "Payment":
        payment = Payment(
            id_=payment_id,
            paid_rubles=payment_paid_rubles,
            start_datetime=current_datetime,
            success=None,
            completion_datetime=None,
            is_cancelled=False,
        )
        tracking.register_new(payment)

        return payment


type PaymentAggregate = Payment
