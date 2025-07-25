from dataclasses import dataclass
from uuid import UUID

from ttt.entities.finance.payment.success import PaymentSuccess


@dataclass(frozen=True)
class PaidStarsPurchasePayment:
    purchase_id: UUID
    user_id: int
    success: PaymentSuccess
