"""
remove `chat_id` columns.

Revision ID: 625c88df7a8b
Revises: 1360cc49b0b6
Create Date: 2025-07-25 05:38:33.567471

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "625c88df7a8b"
down_revision: str | None = "1360cc49b0b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("stars_purchases", "location_chat_id")
    op.drop_column("users", "game_location_chat_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "game_location_chat_id",
            sa.BIGINT(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "stars_purchases",
        sa.Column(
            "location_chat_id",
            sa.BIGINT(),
            autoincrement=False,
            nullable=False,
        ),
    )
    # ### end Alembic commands ###
