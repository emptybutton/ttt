from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentSuccess:
    id: str
    gateway_id: str
