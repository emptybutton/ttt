"""
rename `stars_purchases.new_stars` to `stars_purchases.stars`.

Revision ID: 46880a6a8cff
Revises: b19b4f555d6d
Create Date: 2025-07-02 05:11:35.208443

"""
from collections.abc import Sequence

from alembic import op


revision: str = "46880a6a8cff"
down_revision: str | None = "b19b4f555d6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "stars_purchases",
        "new_stars",
        new_column_name="stars",
    )


def downgrade() -> None:
    op.alter_column(
        "stars_purchases",
        "stars",
        new_column_name="new_stars",
    )
