from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ttt.entities.core.stars_purchase.stars_purchase import (
    StarsPurchase,
    StarsPurchaseAtomic,
)
from ttt.infrastructure.sqlalchemy.tables.common import Base
from ttt.infrastructure.sqlalchemy.tables.payment import TablePayment
from ttt.infrastructure.sqlalchemy.tables.user import TableUser


class TableStarsPurchase(Base[StarsPurchase]):
    __tablename__ = "stars_purchases"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        index=True,
    )
    stars: Mapped[int]
    payment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("payments.id", deferrable=True, initially="DEFERRED"),
    )

    payment: Mapped[TablePayment | None] = relationship(
        TablePayment, lazy="selectin",
    )
    user: Mapped[TableUser] = relationship(TableUser, lazy="selectin")

    __table_args__ = (
        Index(
            "ix_stars_purchases_payment_id",
            payment_id,
            postgresql_where=(payment_id.is_not(None)),
        ),
    )

    def __entity__(self) -> StarsPurchase:
        return StarsPurchase(
            id_=self.id,
            user=self.user.entity(),
            stars=self.stars,
            payment=None if self.payment is None else self.payment.entity(),
        )

    @classmethod
    def of(cls, it: StarsPurchase) -> "TableStarsPurchase":
        return TableStarsPurchase(
            id=it.id_,
            user_id=it.user.id,
            stars=it.stars,
            payment_id=None if it.payment is None else it.payment.id_,
        )


type TableStarsPurchaseAtomic = TableStarsPurchase


def table_stars_purchase_atomic(
    entity: StarsPurchaseAtomic,
) -> TableStarsPurchaseAtomic:
    match entity:
        case StarsPurchase():
            return TableStarsPurchase.of(entity)
