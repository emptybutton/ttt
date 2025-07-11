"""
make `stars_purchases.payment_id` nullable.

Revision ID: 86d75da6c607
Revises: 46880a6a8cff
Create Date: 2025-07-02 05:15:03.842458

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "86d75da6c607"
down_revision: str | None = "46880a6a8cff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("stars_purchases", "payment_id",
               existing_type=sa.UUID(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("stars_purchases", "payment_id",
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###
