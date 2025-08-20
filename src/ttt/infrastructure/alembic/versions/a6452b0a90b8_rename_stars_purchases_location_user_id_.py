"""
rename `stars_purchases.location_user_id` to `stars_purchases.user_id`.

Revision ID: a6452b0a90b8
Revises: 625c88df7a8b
Create Date: 2025-07-25 05:40:56.149110

"""

from collections.abc import Sequence

from alembic import op


revision: str = "a6452b0a90b8"
down_revision: str | None = "625c88df7a8b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "stars_purchases",
        "location_user_id",
        new_column_name="user_id",
    )


def downgrade() -> None:
    op.alter_column(
        "stars_purchases",
        "user_id",
        new_column_name="location_user_id",
    )
