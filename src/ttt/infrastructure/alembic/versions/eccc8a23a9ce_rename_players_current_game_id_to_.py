"""
rename `players.current_game_id` to `players.game_location_game_id`.

Revision ID: eccc8a23a9ce
Revises: 9b894c046d5e
Create Date: 2025-06-19 09:31:46.110425

"""

from collections.abc import Sequence

from alembic import op


revision: str = "eccc8a23a9ce"
down_revision: str | None = "9b894c046d5e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "players",
        "current_game_id",
        new_column_name="game_location_game_id",
    )


def downgrade() -> None:
    op.alter_column(
        "players",
        "game_location_game_id",
        new_column_name="current_game_id",
    )
