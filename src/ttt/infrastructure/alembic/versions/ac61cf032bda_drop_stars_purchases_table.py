"""
drop `stars_purchases` table.

Revision ID: ac61cf032bda
Revises: 58efef109092
Create Date: 2025-06-28 18:41:58.023838

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "ac61cf032bda"
down_revision: str | None = "58efef109092"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("stars_purchases")


def downgrade() -> None:
    op.create_table(
        "stars_purchases",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("payment_gateway_id", sa.String(), nullable=False),
        sa.Column("player_id", sa.BigInteger(), nullable=False),
        sa.Column("stars", sa.Integer(), nullable=False),
        sa.Column("kopecks", sa.Integer(), nullable=False),
        sa.Column("datetime_", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.PrimaryKeyConstraint("id", "payment_gateway_id"),
    )
