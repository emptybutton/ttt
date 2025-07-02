from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.finance.payment.success import PaymentSuccess


@dataclass(frozen=True)
class PaidStarsPurchasePayment:
    purshase_id: UUID
    location: PlayerLocation
    success: PaymentSuccess
