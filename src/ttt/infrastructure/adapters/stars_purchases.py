from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from ttt.application.stars_purchase.ports.stars_purchases import StarsPurchases
from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase
from ttt.infrastructure.sqlalchemy.tables.stars_purchase import (
    TableStarsPurchase,
)


@dataclass(frozen=True, unsafe_hash=False)
class PostgresStarsPurchases(StarsPurchases):
    _session: AsyncSession

    async def stars_purchase_with_id(
        self,
        id_: UUID,
        /,
    ) -> StarsPurchase | None:
        stmt = (
            select(TableStarsPurchase)
            .where(TableStarsPurchase.id == id_)
            .with_for_update()
        )
        table_stars_purchase = await self._session.scalar(stmt)

        if table_stars_purchase is None:
            return None

        return table_stars_purchase.entity()
