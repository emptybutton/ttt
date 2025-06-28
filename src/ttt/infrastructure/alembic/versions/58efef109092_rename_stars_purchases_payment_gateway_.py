"""
rename `stars_purchases.payment_gateway_id` to `stars_purchases.gateway_id`.

Revision ID: 58efef109092
Revises: 3a1d48a54125
Create Date: 2025-06-28 08:50:19.455959

"""
from collections.abc import Sequence

from alembic import op


revision: str = "58efef109092"
down_revision: str | None = "3a1d48a54125"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "stars_purchases",
        "payment_gateway_id",
        new_column_name="gateway_id",
    )


def downgrade() -> None:
    op.alter_column(
        "stars_purchases",
        "gateway_id",
        new_column_name="payment_gateway_id",
    )
