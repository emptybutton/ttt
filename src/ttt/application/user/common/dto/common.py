from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.user.location import UserLocation
from ttt.entities.finance.payment.success import PaymentSuccess


@dataclass(frozen=True)
class PaidStarsPurchasePayment:
    purshase_id: UUID
    location: UserLocation
    success: PaymentSuccess
