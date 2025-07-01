from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from uuid import UUID

from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.assertion import assert_
from ttt.entities.tools.tracking import Tracking


class NoPaidRublesForPaymentError(Exception): ...


class PaymentIsNotPendingError(Exception): ...


class PaymentIsNotInProgressError(Exception): ...


class PaymentState(Enum):
    pending = auto()
    in_progress = auto()
    cancelled = auto()
    completed_successfully = auto()


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
    state: PaymentState

    def __post_init__(self) -> None:
        assert_(self.paid_rubles, else_=NoPaidRublesForPaymentError)

    def be_in_progress(
        self,
        tracking: Tracking,
    ) -> None:
        assert_(
            self.state is PaymentState.pending,
            else_=PaymentIsNotPendingError,
        )

        self.state = PaymentState.in_progress
        tracking.register_mutated(self)

    def complete(
        self,
        success: PaymentSuccess,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> None:
        """
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProgressError:
        """  # noqa: E501

        assert_(
            self.state is PaymentState.in_progress,
            else_=PaymentIsNotInProgressError,
        )

        self.success = success
        self.state = PaymentState.completed_successfully
        self.completion_datetime = current_datetime
        tracking.register_mutated(self)

    def cancel(self, current_datetime: datetime, tracking: Tracking) -> None:
        """
        :raises ttt.entities.finance.payment.payment.PaymentIsNotInProgressError:
        """  # noqa: E501

        assert_(
            self.state is PaymentState.in_progress,
            else_=PaymentIsNotInProgressError,
        )

        self.state = PaymentState.cancelled
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
            state=PaymentState.pending,
        )
        tracking.register_new(payment)

        return payment


type PaymentAggregate = Payment
