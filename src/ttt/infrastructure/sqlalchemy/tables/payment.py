from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from ttt.entities.finance.payment.payment import (
    Payment,
    PaymentAtomic,
    PaymentState,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.entities.finance.rubles import Rubles
from ttt.infrastructure.sqlalchemy.tables.common import Base


class TablePaymentState(StrEnum):
    in_process = "in_process"
    cancelled = "cancelled"
    completed = "completed"

    def entity(self) -> PaymentState:
        match self:
            case TablePaymentState.in_process:
                return PaymentState.in_process
            case TablePaymentState.cancelled:
                return PaymentState.cancelled
            case TablePaymentState.completed:
                return PaymentState.completed

    @classmethod
    def of(cls, it: PaymentState) -> "TablePaymentState":
        match it:
            case PaymentState.in_process:
                return TablePaymentState.in_process
            case PaymentState.cancelled:
                return TablePaymentState.cancelled
            case PaymentState.completed:
                return TablePaymentState.completed


payment_state = postgresql.ENUM(TablePaymentState, name="payment_state")


class TablePayment(Base):
    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    paid_rubles_total_kopecks: Mapped[int] = mapped_column(BigInteger())
    start_datetime: Mapped[datetime]
    completion_datetime: Mapped[datetime | None]
    success_id: Mapped[str | None]
    success_gateway_id: Mapped[str | None]
    state: Mapped[TablePaymentState] = mapped_column(payment_state)

    def entity(self) -> Payment:
        if self.success_id is None or self.success_gateway_id is None:
            success = None
        else:
            success = PaymentSuccess(self.success_id, self.success_gateway_id)

        paid_rubles = Rubles.with_total_kopecks(
            self.paid_rubles_total_kopecks,
        )

        return Payment(
            id_=self.id,
            paid_rubles=paid_rubles,
            start_datetime=self.start_datetime,
            completion_datetime=self.completion_datetime,
            success=success,
            state=self.state.entity(),
        )

    @classmethod
    def of(cls, it: Payment) -> "TablePayment":
        if it.success is None:
            success_id = None
            success_gateway_id = None
        else:
            success_id = it.success.id
            success_gateway_id = it.success.gateway_id

        return TablePayment(
            id=it.id_,
            paid_rubles_total_kopecks=it.paid_rubles.total_kopecks(),
            start_datetime=it.start_datetime,
            completion_datetime=it.completion_datetime,
            success_id=success_id,
            success_gateway_id=success_gateway_id,
            state=TablePaymentState.of(it.state),
        )


type TablePaymentAtomic = TablePayment


def table_payment_atomic(entity: PaymentAtomic) -> TablePaymentAtomic:
    match entity:
        case Payment():
            return TablePayment.of(entity)
