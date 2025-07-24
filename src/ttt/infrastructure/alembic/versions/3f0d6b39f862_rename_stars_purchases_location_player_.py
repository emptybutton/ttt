"""
rename `stars_purchases.location_player_id` to `stars_purchases.location_user_id`.

Revision ID: 3f0d6b39f862
Revises: 50990aed76a8
Create Date: 2025-07-24 05:12:08.982879

"""  # noqa: E501

from collections.abc import Sequence

from alembic import op


revision: str = "3f0d6b39f862"
down_revision: str | None = "50990aed76a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE stars_purchases RENAME CONSTRAINT
        stars_purchases_location_player_id_fkey
        TO stars_purchases_location_user_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_stars_purchases_location_player_id RENAME
        TO ix_stars_purchases_location_user_id;
    """)
    op.alter_column(
        "stars_purchases",
        "location_player_id",
        new_column_name="location_user_id",
    )


def downgrade() -> None:
    op.execute("""
        ALTER TABLE stars_purchases RENAME CONSTRAINT
        stars_purchases_location_user_id_fkey
        TO stars_purchases_location_player_id_fkey;
    """)
    op.execute("""
        ALTER INDEX ix_stars_purchases_location_user_id RENAME
        TO ix_stars_purchases_location_player_id;
    """)
    op.alter_column(
        "stars_purchases",
        "location_user_id",
        new_column_name="location_player_id",
    )
