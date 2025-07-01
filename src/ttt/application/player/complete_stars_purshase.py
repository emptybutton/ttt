from dataclasses import dataclass

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.player.ports.paid_stars_purchase_payment_inbox import (
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.player.ports.player_views import PlayerViews
from ttt.application.player.ports.players import Players
from ttt.entities.finance.payment.payment import PaymentAlreadyCompletedError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CompleteStarsPurshase:
    clock: Clock
    inbox: PaidStarsPurchasePaymentInbox
    players: Players
    transaction: Transaction
    map_: Map
    player_views: PlayerViews

    async def __call__(self) -> None:
        async for paid_payment in self.inbox.stream():
            current_datetime = await self.clock.current_datetime()

            async with self.transaction:
                player = await self.players.player_with_id(
                    paid_payment.location.player_id,
                )

                tracking = Tracking()
                try:
                    player.complete_stars_purchase(
                        paid_payment.purshase_id,
                        paid_payment.success,
                        current_datetime,
                        tracking,
                    )
                except (PaymentAlreadyCompletedError):
                    ...
                else:
                    await self.map_(tracking)
                    await (
                        self.player_views
                        .render_completed_stars_purshase_view(
                            player,
                            paid_payment.purshase_id,
                            paid_payment.location,
                        )
                    )
