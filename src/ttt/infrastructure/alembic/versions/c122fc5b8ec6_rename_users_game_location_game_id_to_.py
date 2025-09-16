"""
rename `users.game_location_game_id` to `users.current_game_id`.

Revision ID: c122fc5b8ec6
Revises: 679c935495d1
Create Date: 2025-09-16 11:10:56.703137

"""

from collections.abc import Sequence

from alembic import op


revision: str = "c122fc5b8ec6"
down_revision: str | None = "679c935495d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users", "game_location_game_id", new_column_name="current_game_id",
    )
    op.execute("""
        ALTER INDEX ix_users_game_location_game_id
        RENAME TO ix_users_current_game_id
    """)
    op.execute("""
        ALTER TABLE users RENAME CONSTRAINT users_game_location_game_id_fkey
        TO users_current_game_id_fkey
    """)


def downgrade() -> None:
    op.alter_column(
        "users", "current_game_id", new_column_name="game_location_game_id",
    )
    op.execute("""
        ALTER INDEX ix_users_current_game_id
        RENAME TO ix_users_game_location_game_id
    """)
    op.execute("""
        ALTER TABLE users RENAME CONSTRAINT users_current_game_id_fkey
        TO users_game_location_game_id_fkey
    """)
