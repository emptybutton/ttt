"""
rename `stars_purchases.user_id` indexes and constraints.

Revision ID: 584168970f91
Revises: a6452b0a90b8
Create Date: 2025-07-25 05:44:18.954130

"""

from collections.abc import Sequence

from alembic import op


revision: str = "584168970f91"
down_revision: str | None = "a6452b0a90b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER INDEX ix_stars_purchases_location_user_id
        RENAME TO ix_stars_purchases_user_id
    """)
    op.execute("""
        ALTER TABLE stars_purchases
        RENAME CONSTRAINT stars_purchases_location_user_id_fkey
        TO stars_purchases_user_id_fkey
    """)


def downgrade() -> None:
    op.execute("""
        ALTER INDEX ix_stars_purchases_user_id
        RENAME TO ix_stars_purchases_location_user_id
    """)
    op.execute("""
        ALTER TABLE stars_purchases
        RENAME CONSTRAINT stars_purchases_user_id_fkey
        TO stars_purchases_location_user_id_fkey
    """)
