from dataclasses import dataclass

from ttt.application.player.ports.paid_stars_purchase_payment_inbox import (
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.player.ports.player_views import PlayerViews
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)


@dataclass(frozen=True, unsafe_hash=False)
class StartStarsPurshasePaymentCompletion:
    inbox: PaidStarsPurchasePaymentInbox
    payment_gateway: StarsPurchasePaymentGateway
    player_views: PlayerViews

    async def __call__(self) -> None:
        async for paid_payment in self.payment_gateway.paid_payment_stream():
            await self.inbox.push(paid_payment)
            await (
                self.player_views
                .render_stars_purchase_will_be_completed_view(
                    paid_payment.location,
                )
            )
