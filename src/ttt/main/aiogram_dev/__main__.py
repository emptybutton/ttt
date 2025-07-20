import asyncio

from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider as DishkaAiogramProvider

from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.infrastructure.buffer import Buffer
from ttt.infrastructure.structlog.logger import (
    DevLoggerFactory,
    LoggerFactory,
)
from ttt.main.aiogram.di import (
    AiogramProvider,
    AiogramRequestDataProvider,
    ApplicationWithAiogramRequestDataProvider,
    ApplicationWithoutAiogramRequestDataProvider,
)
from ttt.main.aiogram.start_aiogram import start_aiogram
from ttt.main.common.di import InfrastructureProvider


async def amain() -> None:
    paid_stars_purchase_payment_buffer = Buffer[PaidStarsPurchasePayment]()

    container_with_request_data = make_async_container(
        DishkaAiogramProvider(),
        AiogramProvider(),
        AiogramRequestDataProvider(),
        ApplicationWithAiogramRequestDataProvider(),
        ApplicationWithoutAiogramRequestDataProvider(),
        InfrastructureProvider(),
        context={
            Buffer[PaidStarsPurchasePayment]: (
                paid_stars_purchase_payment_buffer
            ),
            LoggerFactory: DevLoggerFactory(adds_request_id=True),
        },
    )
    container_without_request_data = make_async_container(
        DishkaAiogramProvider(),
        AiogramProvider(),
        ApplicationWithoutAiogramRequestDataProvider(),
        InfrastructureProvider(),
        context={
            Buffer[PaidStarsPurchasePayment]: (
                paid_stars_purchase_payment_buffer
            ),
            LoggerFactory: DevLoggerFactory(adds_request_id=False),
        },
    )
    await start_aiogram(
        container_with_request_data,
        container_without_request_data,
    )


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
