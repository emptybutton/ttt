from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from uuid import UUID

from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.finance.rubles import Rubles
from ttt.entities.tools.assertion import assert_, not_none
from ttt.entities.tools.tracking import Tracking


class NoPaidRublesForPaymentError(Exception): ...


class NoPaymentError(Exception): ...


class PaymentIsNotInProcessError(Exception): ...


class PaymentIsAlreadyBeingMadeError(Exception): ...


class PaymentState(Enum):
    in_process = auto()
    cancelled = auto()
    completed = auto()


@dataclass
class Payment:
    """
    :raises ttt.entities.finance.payment.payment.NoNewStarsForPaymentError:
    :raises ttt.entities.finance.payment.payment.NoPaidRublesForPaymentError:
    """

    id_: UUID
    paid_rubles: Rubles
    state: PaymentState
    start_datetime: datetime
    completion_datetime: datetime | None
    success: PaymentSuccess | None

    def __post_init__(self) -> None:
        assert_(self.paid_rubles, else_=NoPaidRublesForPaymentError)

    @classmethod
    def start(
        cls,
        payment: "Payment | None",
        payment_id: UUID,
        payment_paid_rubles: Rubles,
        current_datetime: datetime,
        tracking: Tracking,
    ) -> "Payment":
        """
        :raises ttt.entities.finance.payment.payment.PaymentIsAlreadyBeingMadeError:
        """  # noqa: E501

        assert_(payment is None, else_=PaymentIsAlreadyBeingMadeError)

        payment = Payment(
            id_=payment_id,
            paid_rubles=payment_paid_rubles,
            start_datetime=current_datetime,
            state=PaymentState.in_process,
            success=None,
            completion_datetime=None,
        )
        tracking.register_new(payment)

        return payment


def complete_payment(
    payment: Payment | None,
    success: PaymentSuccess,
    current_datetime: datetime,
    tracking: Tracking,
) -> None:
    """
    :raises ttt.entities.finance.payment.payment.NoPaymentError:
    :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
    """

    payment = not_none(payment, else_=NoPaymentError)
    assert_(
        payment.state is PaymentState.in_process,
        else_=PaymentIsNotInProcessError,
    )

    payment.state = PaymentState.completed
    payment.completion_datetime = current_datetime
    payment.success = success
    tracking.register_mutated(payment)


def cancel_payment(
    payment: Payment | None, current_datetime: datetime, tracking: Tracking,
) -> None:
    """
    :raises ttt.entities.finance.payment.payment.NoPaymentError:
    :raises ttt.entities.finance.payment.payment.PaymentIsNotInProcessError:
    """

    payment = not_none(payment, else_=NoPaymentError)
    assert_(
        payment.state is PaymentState.in_process,
        else_=PaymentIsNotInProcessError,
    )

    payment.state = PaymentState.cancelled
    payment.completion_datetime = current_datetime
    tracking.register_mutated(payment)


type PaymentAtomic = Payment
