from dataclasses import dataclass

from ttt.application.stars_purchase.complete_stars_purchase_payment import (
    CompleteStarsPurchasePayment,
)
from ttt.presentation.tasks.task import NextContainer, Task


@dataclass(frozen=True)
class CompleteStarsPurchasePaymentTask(Task):
    async def __call__(self, container: NextContainer) -> None:
        while True:
            async with container() as request:
                complete_stars_purchase_payment = await request.get(
                    CompleteStarsPurchasePayment,
                )
                await complete_stars_purchase_payment()
