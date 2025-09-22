from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.stars_purchase.ports.stars_purchase_tasks import (
    StarsPurchaseTasks,
)
from ttt.entities.finance.payment.success import PaymentSuccess
from ttt.infrastructure.sqlalchemy.tables.stars_purchase import (
    TableStarsPurchase,
)
from ttt.infrastructure.taskiq.tasks.complete_stars_purchase_payment_task import (  # noqa: E501
    complete_stars_purchase_payment_task,
)


@dataclass
class TaskiqStarsPurchaseTasks(StarsPurchaseTasks):
    async def complete_stars_purchase_payment(
        self,
        purchase_id: UUID,
        success: PaymentSuccess,
        /,
    ) -> None:
        await complete_stars_purchase_payment_task.kiq(
            purchase_id,
            success.id,
            success.gateway_id,
        )
